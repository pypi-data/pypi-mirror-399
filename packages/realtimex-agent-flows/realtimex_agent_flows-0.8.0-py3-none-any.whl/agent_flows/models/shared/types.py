"""Common type definitions for executor configurations."""

import json
from typing import Any, Union

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator

from ..flow import FlowStep
from .enums import Combinator, ComparisonOperator, ConditionType
from .validators import CommonValidators, FormKeyValidators, HeaderKeyValidators


class VariableDefinition(BaseModel):
    """Definition of a flow variable."""

    model_config = ConfigDict(extra="allow")

    name: str = Field(..., description="Variable name")
    type: str = Field(
        ..., description="Variable type (string, number, boolean, array, object, null)"
    )
    value: Any = Field(None, description="Variable value")
    description: str = Field("", description="Variable description")
    source: str = Field(
        default="user_input",
        description="Variable source: 'user_input', 'system', or 'node_output'",
    )

    # Apply the common validator
    _validate_name = CommonValidators.validate_variable_name

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate variable type is supported."""
        allowed_types = {"string", "number", "boolean", "array", "object", "null"}
        if v not in allowed_types:
            raise ValueError(
                f"Invalid type '{v}'. Must be one of: {', '.join(sorted(allowed_types))}"
            )
        return v

    @field_validator("value", mode="before")
    @classmethod
    def coerce_value(cls, v: Any, info: ValidationInfo) -> Any:  # noqa: PLR0911
        """Intelligently coerce values to match the specified type."""
        var_type = info.data.get("type") if info.data else None
        if not var_type:
            return v

        # Universal normalization: empty string or None becomes None
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None

        # Type-specific coercion
        if var_type == "string":
            # Empty already normalized to None above
            if isinstance(v, str):
                return v
            # Be conservative: only coerce basic primitives to string
            if isinstance(v, int | float | bool):
                return str(v)
            # For complex types the caller should provide a string explicitly
            return v  # leave as-is; will be caught in final check if needed

        elif var_type == "number":
            # Already a number? Return as-is
            if isinstance(v, int | float):
                return v
            # Try to coerce string to number
            if isinstance(v, str):
                v = v.strip()  # Handle whitespace
                try:
                    # Smart number parsing: use float for decimals/scientific, int otherwise
                    if "." in v or "e" in v.lower() or "E" in v:
                        return float(v)
                    else:
                        return int(v)
                except ValueError:
                    raise ValueError(f"Cannot convert '{v}' to number")  # noqa: B904
            # Other types not supported for number coercion
            raise ValueError(f"Cannot convert {type(v).__name__} to number")

        elif var_type == "boolean":
            # Already boolean? Return as-is
            if isinstance(v, bool):
                return v
            # String boolean representations
            if isinstance(v, str):
                v_lower = v.strip().lower()
                truthy = {"true", "1", "yes", "y", "on", "t"}
                falsy = {"false", "0", "no", "n", "off", "f"}
                if v_lower in truthy:
                    return True
                elif v_lower in falsy:
                    return False
                else:
                    raise ValueError(
                        "String booleans must be one of: true/false, 1/0, yes/no, on/off"
                    )
            # Numeric boolean conversion (0 = False, 1 = True)
            if isinstance(v, int | float):
                # predictable: only 0/1 allowed
                if v == 1:
                    return True
                if v == 0:
                    return False
                raise ValueError("Only numeric 0 or 1 can convert to boolean")
            # Other types not supported
            raise ValueError(f"Cannot convert {type(v).__name__} to boolean")

        elif var_type == "array":
            # Already an array? Return as-is
            if isinstance(v, list):
                return v
            # Try to parse JSON string to array
            if isinstance(v, str):
                v_stripped = v.strip()
                if not v_stripped:  # Empty string already handled above, but being explicit
                    return None
                try:
                    parsed = json.loads(v_stripped)
                    if isinstance(parsed, list):
                        return parsed
                    else:
                        raise ValueError(
                            f"JSON string parses to {type(parsed).__name__}, expected array"
                        )
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON array string: {e}")  # noqa: B904
            # Other types not supported for array coercion
            return v

        elif var_type == "object":
            # Already an object? Return as-is
            if isinstance(v, dict):
                return v
            # Try to parse JSON string to object
            if isinstance(v, str):
                v_stripped = v.strip()
                if not v_stripped:  # Empty string already handled above, but being explicit
                    return None
                try:
                    parsed = json.loads(v_stripped)
                    if isinstance(parsed, dict):
                        return parsed
                    else:
                        raise ValueError(
                            f"JSON string parses to {type(parsed).__name__}, expected object"
                        )
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON object string: {e}")  # noqa: B904
            # Other types not supported for object coercion
            return v

        # For null type and any other cases, let the value pass through
        return v

    @field_validator("value")
    @classmethod
    def validate_value_matches_type(cls, v: Any, info) -> Any:
        """Validate value matches the specified type."""
        var_type = info.data.get("type")
        if var_type is None:
            return v

        # After coercion, enforce strict type checking
        if var_type == "string":
            if v is not None and not isinstance(v, str):
                raise ValueError(f"Expected string or null, got {type(v).__name__}")
        elif var_type == "number":
            if v is not None and not isinstance(v, int | float):
                raise ValueError(f"Expected number or null, got {type(v).__name__}")
        elif var_type == "boolean":
            if v is not None and not isinstance(v, bool):
                raise ValueError(f"Expected boolean or null, got {type(v).__name__}")
        elif var_type == "array":
            if v is not None and not isinstance(v, list):
                raise ValueError(f"Expected array or null, got {type(v).__name__}")
        elif var_type == "object":
            if v is not None and not isinstance(v, dict):
                raise ValueError(f"Expected object or null, got {type(v).__name__}")
        elif var_type == "null" and v is not None:
            raise ValueError(f"Expected null, got {type(v).__name__}: {v}")

        return v


class HeaderDefinition(BaseModel, HeaderKeyValidators):
    """HTTP header definition."""

    key: str = Field(..., description="Header name")
    value: str = Field(..., description="Header value")


class FormDataDefinition(BaseModel, FormKeyValidators):
    """Form data field definition."""

    key: str = Field(..., description="Form field name")
    value: str = Field(..., description="Form field value")


class SimpleCondition(BaseModel):
    """A single condition with variable, operator, and value."""

    model_config = ConfigDict(use_enum_values=True)

    variable: Any = Field(..., description="Variable path to evaluate")
    operator: ComparisonOperator = Field(..., description="Comparison operator")
    value: Any = Field(None, description="Value to compare against")
    type: ConditionType = Field(
        default=ConditionType.AUTO, description="Type to cast values to before comparison"
    )

    # Apply the common validator
    _validate_variable = CommonValidators.validate_variable_path

    @model_validator(mode="after")
    def _normalize_and_validate(self):
        # Operators that do not require a value
        no_value_ops = {
            ComparisonOperator.IS_EMPTY,
            ComparisonOperator.IS_NOT_EMPTY,
        }

        # Normalize: if operator needs no value, ignore any provided value
        if self.operator in no_value_ops:
            self.value = None
            return self
        # For operators that require a value, enforce presence (reject None/empty string)
        if self.value is None or (isinstance(self.value, str) and not self.value.strip()):
            raise ValueError(f"Operator '{self.operator}' requires a non-empty value.")

        # Validate operator compatibility with type
        self._validate_operator_type_compatibility()

        return self

    def _validate_operator_type_compatibility(self):
        """Validate that the operator is compatible with the selected type."""
        # Skip validation for AUTO type as it's permissive
        if self.type == ConditionType.AUTO:
            return

        # String/Array specific operators
        # CONTAINS/NOT_CONTAINS are valid for both STRING and ARRAY
        containment_ops = {
            ComparisonOperator.CONTAINS,
            ComparisonOperator.NOT_CONTAINS,
        }

        # STARTS_WITH/ENDS_WITH are only valid for STRING
        string_ops = {
            ComparisonOperator.STARTS_WITH,
            ComparisonOperator.ENDS_WITH,
        }

        # Numeric/Datetime/Lexicographical operators
        ordering_ops = {
            ComparisonOperator.GREATER_THAN,
            ComparisonOperator.LESS_THAN,
            ComparisonOperator.GREATER_THAN_OR_EQUAL,
            ComparisonOperator.LESS_THAN_OR_EQUAL,
        }

        if self.operator in containment_ops and self.type not in (
            ConditionType.STRING,
            ConditionType.ARRAY,
        ):
            raise ValueError(
                f"Operator '{self.operator}' is only valid for STRING or ARRAY types (got {self.type})"
            )

        if self.operator in string_ops and self.type != ConditionType.STRING:
            raise ValueError(
                f"Operator '{self.operator}' is only valid for STRING type (got {self.type})"
            )

        if self.operator in ordering_ops and self.type not in (
            ConditionType.NUMBER,
            ConditionType.DATETIME,
            ConditionType.STRING,
        ):
            raise ValueError(
                f"Operator '{self.operator}' is only valid for NUMBER, DATETIME, or STRING types (got {self.type})"
            )


class ConditionDefinition(BaseModel):
    """A condition group with combinator and list of conditions."""

    model_config = ConfigDict(use_enum_values=True)

    combinator: Combinator = Field(default=Combinator.AND, description="Logical combinator")
    conditions: list[Union["ConditionDefinition", SimpleCondition]] = Field(
        ..., description="List of conditions or nested condition groups"
    )

    @field_validator("conditions")
    @classmethod
    def validate_conditions_not_empty(cls, v: list) -> list:
        """Validate conditions list is not empty."""
        if not v:
            raise ValueError("Conditions list cannot be empty")
        return v

    @model_validator(mode="after")
    def _apply_defaults_and_validate(self) -> "ConditionDefinition":
        # If combinator omitted and single element, default AND (already defaulted via Field)
        # Additional strictness: when NOT, enforce exactly one child
        if self.combinator == Combinator.NOT and len(self.conditions) != 1:
            raise ValueError("'not' combinator must have exactly one condition")
        return self


class SwitchCase(BaseModel):
    """Definition of a switch case."""

    value: Any = Field(..., description="Value to match against the switch variable")
    blocks: list[FlowStep] = Field(
        default_factory=list, description="Steps to execute if this case matches"
    )

    @field_validator("blocks")
    @classmethod
    def validate_blocks(cls, v: list[FlowStep]) -> list[FlowStep]:
        """Validate that blocks list is not empty."""
        if not v:
            raise ValueError("Switch case must have at least one block")
        return v


class SearchProviderConfig(BaseModel):
    """Base configuration for search providers."""

    model_config = ConfigDict(extra="allow")


class GoogleSearchConfig(SearchProviderConfig):
    """Configuration for Google Custom Search."""

    apiKey: str = Field(..., description="Google Custom Search API key")
    searchEngineId: str = Field(..., description="Custom Search Engine ID")


class BingSearchConfig(SearchProviderConfig):
    """Configuration for Bing Search API."""

    apiKey: str = Field(..., description="Bing Search API subscription key")


class SerpApiConfig(SearchProviderConfig):
    """Configuration for SerpAPI."""

    apiKey: str = Field(..., description="SerpAPI key")


class SerplyConfig(SearchProviderConfig):
    """Configuration for Serply API."""

    apiKey: str = Field(..., description="Serply API key")


class SearXNGConfig(SearchProviderConfig):
    """Configuration for SearXNG instance."""

    baseUrl: str = Field(..., description="SearXNG instance URL")

    # Apply the common validator
    _validate_base_url = CommonValidators.validate_url


class TavilyConfig(SearchProviderConfig):
    """Configuration for Tavily Search API."""

    apiKey: str = Field(..., description="Tavily API key")


class DuckDuckGoConfig(SearchProviderConfig):
    """Configuration for DuckDuckGo (no config required)."""

    pass


class SearchProviderDefinition(BaseModel):
    """Definition of a search provider with configuration."""

    model_config = ConfigDict(extra="allow")

    name: str = Field(..., description="Provider name")
    config: dict[str, Any] = Field(
        default_factory=dict, description="Provider-specific configuration"
    )

    @field_validator("name")
    @classmethod
    def validate_provider_name(cls, v: str) -> str:
        """Validate provider name is supported."""
        from .enums import SearchProvider

        if v not in [provider.value for provider in SearchProvider]:
            valid_providers = [provider.value for provider in SearchProvider]
            raise ValueError(
                f"Invalid provider '{v}'. Must be one of: {', '.join(valid_providers)}"
            )
        return v


__all__ = [
    "VariableDefinition",
    "HeaderDefinition",
    "FormDataDefinition",
    "SimpleCondition",
    "ConditionDefinition",
    "SwitchCase",
    "SearchProviderConfig",
    "GoogleSearchConfig",
    "BingSearchConfig",
    "SerpApiConfig",
    "SerplyConfig",
    "SearXNGConfig",
    "TavilyConfig",
    "DuckDuckGoConfig",
    "SearchProviderDefinition",
]
