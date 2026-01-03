"""Expression-based variable interpolation utilities."""

import json
import logging
import re
from typing import Any

import jmespath
from simpleeval import simple_eval

logger = logging.getLogger(__name__)


class VariableInterpolator:
    """Handles expression-based variable interpolation in strings using {{ }} syntax."""

    def __init__(self) -> None:
        """Initialize the expression interpolator."""
        self._expression_pattern = re.compile(r"\{\{\s*([^}]+)\s*\}\}")
        self._variable_pattern = re.compile(
            r"\$([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*|\[[^\]]+\])*)"
        )
        self._functions = {
            "jsonPath": self._json_path,
            "jmespath": self._jmes_path,
            "len": len,
            "toJson": json.dumps,
            "toString": str,
            "upper": str.upper,
            "lower": str.lower,
            "strip": str.strip,
        }

    def interpolate(self, text: str, variables: dict[str, Any]) -> str:
        """Replace {{ expression }} patterns with evaluated values.

        Args:
            text: Text containing expression patterns
            variables: Variable values

        Returns:
            Text with expressions evaluated and replaced
        """
        if not isinstance(text, str):
            return text

        def replace_expression(match: re.Match[str]) -> str:
            expression = match.group(1).strip()
            try:
                result = self._evaluate_expression(expression, variables)
                # Convert complex objects to JSON strings for text interpolation
                if isinstance(result, dict | list):
                    return json.dumps(result)
                return str(result)
            except Exception as e:
                logger.warning(f"Expression evaluation failed: '{expression}' - {e}")
                return match.group(0)

        result = self._expression_pattern.sub(replace_expression, text)

        if result != text:
            logger.debug(f"Interpolated: '{text}' -> '{result}'")

        return result

    def interpolate_object(self, obj: Any, variables: dict[str, Any]) -> Any:
        """Recursively interpolate expressions in an object structure.

        Args:
            obj: Object to interpolate (can be dict, list, string, or primitive)
            variables: Variable values

        Returns:
            Object with expressions interpolated
        """
        if isinstance(obj, str):
            if self._is_single_expression(obj):
                expression = self._extract_single_expression(obj)
                try:
                    return self._evaluate_expression(expression, variables)
                except Exception as e:
                    logger.warning(f"Expression evaluation failed: '{expression}' - {e}")
                    return obj
            else:
                return self.interpolate(obj, variables)
        elif isinstance(obj, dict):
            return {key: self.interpolate_object(value, variables) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.interpolate_object(item, variables) for item in obj]
        else:
            return obj

    def extract_variables(self, text: str) -> list[str]:
        """Extract all variable references from expressions in text.

        Args:
            text: Text to scan for variable references

        Returns:
            List of variable names found (without $ prefix)
        """
        if not isinstance(text, str):
            return []

        variables = set()
        matches = self._expression_pattern.findall(text)

        for expression in matches:
            var_matches = self._variable_pattern.findall(expression)
            variables.update(var_matches)

        return list(variables)

    def has_variables(self, text: str) -> bool:
        """Check if text contains any expression patterns.

        Args:
            text: Text to check

        Returns:
            True if text contains expressions
        """
        if not isinstance(text, str):
            return False

        return bool(self._expression_pattern.search(text))

    def _evaluate_expression(self, expression: str, variables: dict[str, Any]) -> Any:
        """Evaluate a single expression with variable context.

        Args:
            expression: Expression to evaluate
            variables: Variable context

        Returns:
            Evaluated result
        """
        expression = expression.strip()

        # Handle simple variable reference: $variable.path
        if expression.startswith("$") and not self._contains_function_call(expression):
            var_path = expression[1:]  # Remove $
            value = self._get_variable_value(var_path, variables)
            if value is None:
                raise ValueError(f"Variable not found: {var_path}")
            return value

        # Replace $variable references with valid Python variable names and create context
        processed_expression, context = self._prepare_expression_for_eval(expression, variables)

        try:
            return simple_eval(processed_expression, names=context, functions=self._functions)
        except Exception as e:
            logger.debug(f"Expression evaluation failed: {e}")
            raise

    def _contains_function_call(self, expression: str) -> bool:
        """Check if expression contains function calls.

        Args:
            expression: Expression to check

        Returns:
            True if expression contains function calls
        """
        return "(" in expression and ")" in expression

    def _prepare_expression_for_eval(
        self, expression: str, variables: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Prepare expression for evaluation by replacing $variables with valid Python names.

        Args:
            expression: Original expression
            variables: Variable context

        Returns:
            Tuple of (processed_expression, context_dict)
        """
        context = {}
        processed_expression = expression
        var_counter = 0

        # Find all variable references and replace them
        def replace_variable(match: re.Match[str]) -> str:
            nonlocal var_counter
            var_path = match.group(1)
            value = self._get_variable_value(var_path, variables)

            if value is not None:
                # Create a valid Python variable name
                var_name = f"var_{var_counter}"
                var_counter += 1
                context[var_name] = value
                return var_name
            else:
                # Variable not found, this will cause the expression to fail
                raise ValueError(f"Variable not found: {var_path}")

        processed_expression = self._variable_pattern.sub(replace_variable, processed_expression)

        return processed_expression, context

    def _get_variable_value(self, path: str, variables: dict[str, Any]) -> Any:
        """Get variable value using JMESPath.

        Args:
            path: Variable path (e.g., "store.bicycle.color")
            variables: Variable context

        Returns:
            Variable value or None if not found
        """
        try:
            return jmespath.search(path, variables)
        except Exception as e:
            logger.debug(f"JMESPath variable resolution failed for '{path}': {e}")
            return None

    def _is_single_expression(self, text: str) -> bool:
        """Check if the entire string is a single expression.

        Args:
            text: Text to check

        Returns:
            True if text is exactly "{{ expression }}" format
        """
        if not isinstance(text, str):
            return False

        return bool(self._expression_pattern.fullmatch(text))

    def _extract_single_expression(self, text: str) -> str:
        """Extract expression from a single expression string.

        Args:
            text: Text in format "{{ expression }}"

        Returns:
            Expression without the {{ }} wrapper
        """
        match = self._expression_pattern.fullmatch(text)
        if match:
            return match.group(1).strip()
        return ""

    def _json_path(self, obj: Any, path: str) -> Any:
        """JSONPath function for complex object queries.

        Args:
            obj: Object to query
            path: JSONPath expression

        Returns:
            Query result or None if not found
        """
        try:
            from jsonpath_ng import parse as jsonpath_parse

            if not path.startswith("$"):
                path = f"$.{path}"

            jsonpath_expr = jsonpath_parse(path)
            matches = jsonpath_expr.find(obj)

            if not matches:
                return None
            elif len(matches) == 1:
                return matches[0].value
            else:
                return [match.value for match in matches]

        except Exception as e:
            logger.debug(f"JSONPath error for '{path}': {e}")
            return None

    def _jmes_path(self, obj: Any, path: str) -> Any:
        """JMESPath function for object queries.

        Args:
            obj: Object to query
            path: JMESPath expression

        Returns:
            Query result or None if not found
        """
        try:
            return jmespath.search(path, obj)
        except Exception as e:
            logger.debug(f"JMESPath error for '{path}': {e}")
            return None
