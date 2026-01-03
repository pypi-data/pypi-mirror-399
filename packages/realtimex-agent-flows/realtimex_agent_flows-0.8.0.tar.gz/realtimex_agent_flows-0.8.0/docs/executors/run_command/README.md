# Run Command Executor

Execute CLI commands via subprocess and capture the output. Commands run without a shell by default for safety and predictability.

## Overview

- **Executor type**: `runCommand`
- **Purpose**: Execute CLI commands and capture output for downstream processing
- **Use cases**: Build scripts, git operations, file manipulation, system utilities

## Configuration Schema

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `command` | string | — | **Required.** The executable to run. |
| `args` | list\<string\> | `[]` | Arguments to pass to the command. |
| `cwd` | string \| `null` | `null` | Working directory for execution. |
| `env` | object | `{}` | Environment variables to add (merged with existing). |
| `timeout` | integer | `30` | Execution timeout in seconds. |
| `maxRetries` | integer | `0` | Retry attempts on failure. |
| `resultVariable` | string \| `null` | `null` | Flow variable to store the result. |
| `directOutput` | boolean | `false` | If `true`, return result as flow output. |

## Result Handling

The executor captures stdout and extracts the result:

1. **Structured output**: If stdout contains `<output>...</output>`, the content is extracted and parsed as JSON if valid.
2. **Plain output**: Otherwise, trimmed stdout becomes the result.

### Example Structured Output

Script:
```bash
echo "<output>{\"status\": \"success\", \"count\": 42}</output>"
```

Result stored in `resultVariable`:
```json
{"status": "success", "count": 42}
```

## Usage

### Basic Command
```json
{
  "type": "runCommand",
  "config": {
    "command": "echo",
    "args": ["Hello, World!"],
    "resultVariable": "greeting"
  }
}
```

### With Environment Variables
```json
{
  "type": "runCommand",
  "config": {
    "command": "npm",
    "args": ["run", "build"],
    "cwd": "/app",
    "env": {
      "NODE_ENV": "production",
      "CI": "true"
    },
    "timeout": 300,
    "resultVariable": "build_output"
  }
}
```

### Shell Features (Pipes, Redirects)

For commands requiring shell features, use the `sh -c` pattern:

```json
{
  "type": "runCommand",
  "config": {
    "command": "sh",
    "args": ["-c", "cat data.json | jq '.name'"],
    "resultVariable": "name"
  }
}
```

### Structured JSON Output
```json
{
  "type": "runCommand",
  "config": {
    "command": "python3",
    "args": ["-c", "print('<output>{\"computed\": 123}</output>')"],
    "resultVariable": "result"
  }
}
```

## Execution Behavior

1. **Validation**: Validates config, interpolates variables in `command`, `args`, `cwd`, `env`.
2. **Execution**: Spawns subprocess without shell (safer, more predictable).
3. **Capture**: Collects stdout and stderr.
4. **Extraction**: Extracts `<output>...</output>` content or uses trimmed stdout.
5. **Assignment**: Stores result in `resultVariable` if specified.

### Failure Conditions

| Condition | Behavior |
|-----------|----------|
| Non-zero exit code | Step fails with exit code and stderr/stdout message. |
| Timeout exceeded | Step fails after `timeout` seconds. |
| Missing `command` | Step fails at validation. |

