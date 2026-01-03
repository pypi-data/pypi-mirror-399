# Conditional Executor

The **Conditional Executor** enables branching logic within Agent Flows, executing different blocks based on condition evaluation. This executor is essential for implementing decision trees, validation logic, and dynamic flow routing based on variable values.

## Overview

**Executor Type**: `conditional`
**Purpose**: Execute different blocks based on condition evaluation.
**Use Cases**: Decision trees, validation logic, dynamic routing, error handling.

## Core Concept

The Conditional Executor evaluates a condition against flow variables and executes either `truePath` or `falsePath` based on the result. It supports comprehensive comparison operators, nested variable access, and **strict type checking** for robust logic.

## Configuration

The executor is configured via the `config` object in a flow step.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `condition`  | `object` | Yes | - | The condition logic to evaluate. Can be a single comparison or a group. |
| `truePath`   | `array`  | No | `[]` | List of steps to execute if the condition evaluates to `true`. |
| `falsePath`  | `array`  | No | `[]` | List of steps to execute if the condition evaluates to `false`. |

## Condition Structure

The `condition` field **always** uses a unified structure consisting of a `combinator` and a list of `conditions`.

```json
{
  "combinator": "and",
  "conditions": [
    {
      "variable": "{{ $user.age }}",
      "operator": "greater_than_or_equal",
      "value": 18,
      "type": "number"
    }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `combinator` | `enum` | Yes | Logical operator: `and`, `or`, `not`. |
| `conditions` | `Condition[]` | Yes | List of simple conditions or nested groups. |

### Simple Condition Item

Each item in the `conditions` array is a comparison object:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `variable` | `any` | Yes | The left-side operand. Supports interpolation (e.g., `{{ $var }}`). |
| `operator` | `enum` | Yes | The comparison operator (see below). |
| `value` | `any` | Yes* | The right-side operand. *Ignored for `is_empty`/`is_not_empty`.* |
| `type` | `enum` | No | The data type to enforce for comparison. Default: `auto`. |

## Type System

The `type` field controls how values are treated during comparison.

| Type | Behavior | Strictness |
|------|----------|------------|
| `auto` | **Legacy/Default.** Attempts to infer types. Tries numeric comparison first, falls back to string. | Permissive |
| `string` | Treats both operands as strings. | **Strict** |
| `number` | Expects numbers (int/float). Raises error if operands are strings/bools. | **Strict** |
| `boolean`| Expects booleans. Raises error if operands are strings/numbers. | **Strict** |
| `datetime`| Parses strings (ISO 8601) or timestamps into datetime objects. | Parsing |
| `array` | Expects arrays (lists). Parses JSON strings if necessary. | **Strict** |
| `object` | Expects objects (dictionaries). Parses JSON strings if necessary. | **Strict** |

> [!IMPORTANT]
> **Strict Types**: When using `string`, `number`, `boolean`, `array`, or `object`, the system **does not** implicitly cast values. If the variable `{{ $input }}` is the string `"123"` and you use `type: "number"`, the execution will fail with a `ValueError`. You must ensure your data types match.

## Operators

| Operator | Supported Types | Description |
|----------|-----------------|-------------|
| `equals`, `not_equals` | All | Checks equality. |
| `is_empty`, `is_not_empty` | All | Checks if value is null, empty string, or empty collection. |
| `greater_than`, `less_than`, `greater_than_or_equal`, `less_than_or_equal` | `number`, `datetime`, `string`*, `auto` | *String comparison is lexicographical.* |
| `contains`, `not_contains` | `string`, `array`, `auto` | Checks if value exists in string/array. |
| `starts_with`, `ends_with` | `string` | Checks string prefix/suffix. **Invalid for arrays.** |

## Configuration Examples

### Basic Condition Example
```json
{
  "type": "conditional",
  "config": {
    "condition": {
      "combinator": "and",
      "conditions": [
        { "variable": "{{ $user_type }}", "operator": "equals", "value": "premium", "type": "string" }
      ]
    },
    "truePath": [
      {
        "type": "apiCall",
        "config": {
          "url": "https://api.example.com/premium-features",
          "method": "GET",
          "responseVariable": "premium_features"
        }
      }
    ],
    "falsePath": [ ... ]
  }
}
```

### OR Logic Example
```json
{
  "type": "conditional",
  "config": {
    "condition": {
      "combinator": "or",
      "conditions": [
        { "variable": "{{ $user.role }}", "operator": "equals", "value": "admin", "type": "string" },
        { "variable": "{{ $user.role }}", "operator": "equals", "value": "moderator", "type": "string" }
      ]
    },
    "truePath": [ ... ]
  }
}
```

### Numeric Comparison
```json
{
  "type": "conditional",
  "config": {
    "condition": {
      "combinator": "and",
      "conditions": [
        { "variable": "{{ $subscription_count }}", "operator": "greater_than", "value": 0, "type": "number" }
      ]
    },
    "truePath": [ ... ]
  }
}
```

### Nested Variable Access
```json
{
  "type": "conditional",
  "config": {
    "condition": {
      "combinator": "and",
      "conditions": [
        { "variable": "{{ $user.profile.status }}", "operator": "equals", "value": "active", "type": "string" }
      ]
    },
    "truePath": [ ... ]
  }
}
```

## Execution Behavior

### Condition Evaluation Flow
1. **Variable Resolution**: Extract variable value using nested path access.
2. **Value Interpolation**: Resolve `{{ $variable.key }}` references in comparison value.
   > **Note**: The syntax for variable interpolation is `{{ $variable_name }}`. For nested properties, use dot notation like `{{ $user.profile.age }}`.
3. **Type Validation**: **(New)** If a strict `type` is specified, validate that operands match the type.
4. **Operator Application**: Apply the specified comparison operator.
5. **Block Selection**: Choose `truePath` or `falsePath` based on the result.
6. **Block Execution**: Execute selected blocks sequentially.

### Error Handling
- **Type Mismatches**: If `type` is strict (e.g., `number`) and operands do not match (e.g., string "123"), a `ValueError` is raised.
- **Condition Errors**: Invalid variable paths or operator failures terminate execution.
- **Block Failures**: First block failure terminates the conditional execution.

## Advanced Patterns

### Nested Conditionals
```json
{
  "type": "conditional",
  "config": {
    "condition": {
      "combinator": "and",
      "conditions": [
        { "variable": "{{ $status }}", "operator": "contains", "value": "error", "type": "string" }
      ]
    },
    "truePath": [
      {
        "type": "conditional",
        "config": {
          "condition": {
            "combinator": "and",
            "conditions": [
              { "variable": "{{ $error.code }}", "operator": "equals", "value": 500, "type": "number" }
            ]
          },
          "truePath": [ ... ],
          "falsePath": [ ... ]
        }
      }
    ]
  }
}
```
