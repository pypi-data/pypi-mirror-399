"""Condition evaluation logic for reuse across executors."""

import operator as op
from typing import Any

import structlog

from agent_flows.core.resources import VariableInterpolator
from agent_flows.models.shared import (
    Combinator,
    ComparisonOperator,
    ConditionDefinition,
    ConditionType,
    SimpleCondition,
)

logger = structlog.get_logger(__name__)


class ConditionEvaluator:
    """Evaluates conditions with support for combinators and nested conditions."""

    def __init__(self):
        """Initialize the condition evaluator."""
        self.interpolator = VariableInterpolator()

    async def evaluate(
        self, condition: ConditionDefinition | SimpleCondition, variables: dict[str, Any]
    ) -> bool:
        """Evaluate a condition definition against variables.

        Args:
            condition: Condition definition to evaluate
            variables: Variables dictionary for evaluation

        Returns:
            Boolean result of condition evaluation

        Raises:
            ValueError: If condition evaluation fails
        """
        try:
            if isinstance(condition, SimpleCondition):
                return await self._evaluate_simple_condition(condition, variables)
            return await self._evaluate_condition_group(condition, variables)
        except Exception as e:
            raise ValueError(f"Failed to evaluate condition: {str(e)}") from e

    async def _evaluate_condition_group(
        self, condition_group: ConditionDefinition, variables: dict[str, Any]
    ) -> bool:
        """Evaluate a condition group with combinator.

        Args:
            condition_group: Condition group to evaluate
            variables: Variables dictionary for evaluation

        Returns:
            Boolean result of condition group evaluation
        """
        combinator = condition_group.combinator
        conditions = condition_group.conditions

        logger.debug(
            "Evaluating condition group",
            combinator=combinator,
            conditions_count=len(conditions),
        )

        # Evaluate each condition in the group
        results = []
        for i, sub_condition in enumerate(conditions):
            try:
                if isinstance(sub_condition, SimpleCondition):
                    result = await self._evaluate_simple_condition(sub_condition, variables)
                elif isinstance(sub_condition, ConditionDefinition):
                    result = await self._evaluate_condition_group(sub_condition, variables)
                else:
                    raise ValueError(f"Unsupported condition type: {type(sub_condition)}")

                results.append(result)

                logger.debug(
                    "Sub-condition evaluated",
                    condition_index=i,
                    condition_type=type(sub_condition).__name__,
                    result=result,
                )

            except Exception as e:
                raise ValueError(f"Failed to evaluate sub-condition {i}: {str(e)}") from e

        # Apply combinator logic
        if combinator == Combinator.AND:
            final_result = all(results)
        elif combinator == Combinator.OR:
            final_result = any(results)
        elif combinator == Combinator.NOT:
            # 'not' should have exactly one condition (validated in ConditionDefinition)
            final_result = not results[0]
        else:
            raise ValueError(f"Unsupported combinator: {combinator}")

        logger.debug(
            "Condition group evaluated",
            combinator=combinator,
            individual_results=results,
            final_result=final_result,
        )

        return final_result

    async def _evaluate_simple_condition(
        self, condition: SimpleCondition, variables: dict[str, Any]
    ) -> bool:
        """Evaluate a single condition.

        Args:
            condition: Simple condition to evaluate
            variables: Variables dictionary for evaluation

        Returns:
            Boolean result of condition evaluation
        """
        # Use interpolator for {{...}} format variable resolution
        variable_value = self.interpolator.interpolate_object(condition.variable, variables)

        # If interpolation returned the original string unchanged, variable was not found
        if (
            variable_value == condition.variable
            and isinstance(condition.variable, str)
            and condition.variable.strip().startswith("{{")
            and condition.variable.strip().endswith("}}")
        ):
            raise ValueError(f"Variable '{condition.variable}' not found in execution context")

        # Interpolate the comparison value (supports strings, objects, and complex templates)
        comparison_value = self.interpolator.interpolate_object(condition.value, variables)

        # Evaluate based on operator
        logger.debug(
            "Evaluating simple condition",
            variable=condition.variable,
            variable_value=variable_value,
            operator=condition.operator,
            comparison_value=comparison_value,
            type=condition.type,
        )

        # Cast values to the specified type
        try:
            from agent_flows.utils.type_casting import cast_value

            casted_variable_value = cast_value(variable_value, condition.type)
            casted_comparison_value = cast_value(comparison_value, condition.type)
        except ValueError as e:
            # If casting fails, we can either fail hard or return False.
            # Failing hard is safer for explicit type checks.
            raise ValueError(f"Type casting failed: {str(e)}") from e

        # If type is AUTO, use the legacy smart comparison logic (which is embedded in _apply_operator)
        # If type is strict, we should ideally bypass the smart logic in _apply_operator,
        # but _apply_operator currently tries numeric conversion first.
        # To enforce strictness, we can rely on the fact that we've already casted them.
        # However, _apply_operator might try to re-cast strings to numbers if they look like numbers.
        # For strict STRING type, we want "123" == "123" (string comparison), not 123 == 123 (numeric).
        # We need to pass the type hint to _apply_operator or handle it here.

        return self._apply_operator(
            casted_variable_value,
            condition.operator,
            casted_comparison_value,
            strict_type=condition.type if condition.type != ConditionType.AUTO else None,
        )

    def _is_empty(self, v: Any) -> bool:
        """Check if a value is considered empty."""
        # None is empty
        if v is None:
            return True
        # Strings: empty after stripping
        if isinstance(v, str):
            return len(v.strip()) == 0
        # Collections: empty containers
        if isinstance(v, list | tuple | set | dict):
            return len(v) == 0
        # Everything else (numbers, booleans) are NOT "empty"
        return False

    def _apply_operator(  # noqa: PLR0911
        self,
        variable_value: Any,
        operator: ComparisonOperator,
        comparison_value: Any,
        strict_type: ConditionType | None = None,
    ) -> bool:
        """Apply comparison operator to values.

        Args:
            variable_value: Value from variable (can be None if variable not found)
            operator: Comparison operator
            comparison_value: Value to compare against
            strict_type: If provided, bypasses smart type inference and uses direct comparison

        Returns:
            Boolean result of comparison

        Raises:
            ValueError: If operator is not supported or comparison fails
        """
        try:
            # Handle empty/null checks first (don't need type conversion)
            if operator == ComparisonOperator.IS_EMPTY:
                return self._is_empty(variable_value)

            elif operator == ComparisonOperator.IS_NOT_EMPTY:
                return not self._is_empty(variable_value)

            # If strict type is provided, use direct comparison helper
            if strict_type:
                return self._compare_values_strict(
                    variable_value, comparison_value, operator, strict_type
                )

            # Legacy "smart" logic (AUTO mode)
            # For other operators, handle different data types appropriately
            elif operator == ComparisonOperator.EQUALS:
                return self._compare_values(variable_value, comparison_value, "==")

            elif operator == ComparisonOperator.NOT_EQUALS:
                return self._compare_values(variable_value, comparison_value, "!=")

            elif operator == ComparisonOperator.GREATER_THAN:
                return self._compare_values(variable_value, comparison_value, ">")

            elif operator == ComparisonOperator.LESS_THAN:
                return self._compare_values(variable_value, comparison_value, "<")

            elif operator == ComparisonOperator.GREATER_THAN_OR_EQUAL:
                return self._compare_values(variable_value, comparison_value, ">=")

            elif operator == ComparisonOperator.LESS_THAN_OR_EQUAL:
                return self._compare_values(variable_value, comparison_value, "<=")

            # String operations (always convert to strings)
            elif operator == ComparisonOperator.CONTAINS:
                if isinstance(variable_value, list | tuple | set):
                    return comparison_value in variable_value
                return str(comparison_value) in str(variable_value)

            elif operator == ComparisonOperator.NOT_CONTAINS:
                if isinstance(variable_value, list | tuple | set):
                    return comparison_value not in variable_value
                return str(comparison_value) not in str(variable_value)

            elif operator == ComparisonOperator.STARTS_WITH:
                return str(variable_value).startswith(str(comparison_value))

            elif operator == ComparisonOperator.ENDS_WITH:
                return str(variable_value).endswith(str(comparison_value))

            else:
                raise ValueError(f"Unsupported operator: {operator}")

        except Exception as e:
            raise ValueError(f"Failed to apply operator {operator}: {str(e)}") from e

    def _compare_values_strict(
        self,
        value1: Any,
        value2: Any,
        operator: ComparisonOperator,
        strict_type: ConditionType,
    ) -> bool:
        """Compare two values using strict typing (no implicit conversion)."""
        # Map enum to python operators
        op_map = {
            ComparisonOperator.EQUALS: op.eq,
            ComparisonOperator.NOT_EQUALS: op.ne,
            ComparisonOperator.GREATER_THAN: op.gt,
            ComparisonOperator.LESS_THAN: op.lt,
            ComparisonOperator.GREATER_THAN_OR_EQUAL: op.ge,
            ComparisonOperator.LESS_THAN_OR_EQUAL: op.le,
        }

        # Handle sequence operators separately
        if operator == ComparisonOperator.CONTAINS:
            return value2 in value1  # value1 is container
        if operator == ComparisonOperator.NOT_CONTAINS:
            return value2 not in value1
        if operator == ComparisonOperator.STARTS_WITH:
            return value1.startswith(value2)
        if operator == ComparisonOperator.ENDS_WITH:
            return value1.endswith(value2)

        if operator not in op_map:
            raise ValueError(f"Operator {operator} not supported for strict comparison")

        python_op = op_map[operator]

        # For strict comparison, we trust the values are already casted
        # But we still need to handle potential type mismatches that Python would reject (e.g. str < int)
        try:
            return python_op(value1, value2)
        except TypeError as e:
            # If types are incompatible for ordering, raise clear error
            raise ValueError(
                f"Cannot compare {type(value1).__name__} and {type(value2).__name__} "
                f"with operator {operator}"
            ) from e

    def _compare_values(self, value1: Any, value2: Any, operator: str) -> bool:
        """Compare two values with intelligent type handling.

        Args:
            value1: First value to compare
            value2: Second value to compare
            operator: Comparison operator as string

        Returns:
            Boolean result of comparison

        Raises:
            ValueError: If comparison cannot be performed
        """
        from agent_flows.utils.type_casting import to_datetime, to_number

        # Define operator mappings
        numeric_ops = {"==": op.eq, "!=": op.ne, ">": op.gt, "<": op.lt, ">=": op.ge, "<=": op.le}

        equality_ops = {"==": op.eq, "!=": op.ne}
        relational_ops = {">": op.gt, "<": op.lt, ">=": op.ge, "<=": op.le}

        if operator not in numeric_ops:
            raise ValueError(f"Unsupported operator: {operator}")

        # Try numeric comparison first
        try:
            num1 = to_number(value1)
            num2 = to_number(value2)
            return numeric_ops[operator](num1, num2)
        except (ValueError, TypeError):
            pass

        # For equality operators, allow string fallback
        if operator in equality_ops:
            str1 = str(value1)
            str2 = str(value2)
            return equality_ops[operator](str1, str2)

        # For relational operators, try datetime comparison
        if operator in relational_ops:
            try:
                dt1 = to_datetime(value1)
                dt2 = to_datetime(value2)
                return relational_ops[operator](dt1, dt2)
            except (ValueError, TypeError, ImportError) as e:
                raise ValueError(
                    f"Cannot perform relational comparison '{operator}' between "
                    f"'{value1}' (type: {type(value1).__name__}) and "
                    f"'{value2}' (type: {type(value2).__name__}). "
                    f"Values must be numeric or valid datetime strings."
                ) from e

        # This should never be reached due to the initial operator check
        raise ValueError(f"Cannot perform comparison with operator {operator}")
