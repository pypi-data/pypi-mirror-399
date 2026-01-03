# SetVariables Executor

The **SetVariables Executor** allows you to define, update, and manage variables within the flow execution context. It supports creating new variables, updating existing ones, setting nested properties via dot notation, and enforcing strict data types.

## Overview

**Executor Type**: `setVariables`
**Purpose**: Manage flow state by setting variable values.
**Use Cases**:
- Initializing default values.
- Transforming data (e.g., casting strings to numbers).
- Extracting specific fields from complex objects.
- Preparing data for subsequent steps.

## Configuration

The executor is configured via the `config` object.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `variables` | `array` | Yes | A list of variable assignments to perform. |

### Variable Assignment Object

Each item in the `variables` array defines a single assignment.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | `string` | Yes | - | The variable name. Supports dot notation for nested paths (e.g., `user.profile.age`). |
| `value` | `any` | Yes | - | The value to assign. Supports interpolation (e.g., `{{ $input.age }}`). |
| `type` | `enum` | No | `auto` | The target data type. See **Type System** below. |

## Features

### 1. Variable Interpolation
You can reference existing variables in the `value` field using the `{{ $variable_name }}` syntax.

```json
{
  "name": "greeting",
  "value": "Hello, {{ $user.name }}!"
}
```

### 2. Nested Path Support
Use dot notation in the `name` field to set values deep within objects. If the parent objects do not exist, they will be created automatically.

```json
{
  "name": "user.settings.theme",
  "value": "dark"
}
```
*Resulting Context:*
```json
{
  "user": {
    "settings": {
      "theme": "dark"
    }
  }
}
```

### 3. Strict Type Checking
The `type` field allows you to enforce and cast data types. This uses the same strict typing system as the Conditional Executor.

| Type | Behavior |
|------|----------|
| `auto` | Default. No casting is performed unless necessary. |
| `string` | Ensures the value is a string. |
| `number` | Casts to int/float. Errors if conversion fails. |
| `boolean`| Casts to boolean. |
| `datetime`| Parses ISO strings or timestamps into datetime objects. |
| `array` | Ensures the value is a list. |
| `object` | Ensures the value is a dictionary. |

**Example: Casting a String to a Number**
If `{{ $input_string }}` is `"123.45"`:
```json
{
  "name": "amount",
  "value": "{{ $input_string }}",
  "type": "number"
}
```
*Result:* `amount` will be the number `123.45`.

## Examples

### Basic Initialization
Initialize variables at the start of a flow.

```json
{
  "type": "setVariables",
  "config": {
    "variables": [
      { "name": "count", "value": 0, "type": "number" },
      { "name": "status", "value": "pending", "type": "string" }
    ]
  }
}
```

### Data Transformation
Extract and cast data from an API response.

```json
{
  "type": "setVariables",
  "config": {
    "variables": [
      {
        "name": "order_total",
        "value": "{{ $api_response.data.total_amount }}",
        "type": "number"
      },
      {
        "name": "order_date",
        "value": "{{ $api_response.data.created_at }}",
        "type": "datetime"
      }
    ]
  }
}
```

### Complex Object Creation
Build a structured object for a downstream API call.

```json
{
  "type": "setVariables",
  "config": {
    "variables": [
      { "name": "payload.user_id", "value": "{{ $user.id }}" },
      { "name": "payload.metadata.source", "value": "flow_execution" },
      { "name": "payload.metadata.timestamp", "value": "{{ $system.timestamp }}" }
    ]
  }
}
```
