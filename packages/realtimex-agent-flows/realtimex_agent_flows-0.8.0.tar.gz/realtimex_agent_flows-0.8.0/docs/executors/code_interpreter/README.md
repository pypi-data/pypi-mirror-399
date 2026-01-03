# Code Interpreter Executor

Execute short Python scripts through the local interpreter service and return the structured result back into your flow. This milestone ships with Python-only support wired to `http://127.0.0.1:8004/python-interpreter/run`.

## Overview

- **Executor type**: `codeInterpreter`
- **Purpose**: run lightweight Python snippets for data prep, ad-hoc API calls, or glue logic between steps
- **Great for**:
  - Normalising API responses before handing them to an LLM
  - Performing quick calculations or transformations without spinning up external services
  - Experimenting with utility code alongside declarative flows

## Execution Flow

1. The step configuration is validated and variables are interpolated.
2. When dependencies are provided and the script lacks a header, the executor injects a uv-compatible dependency block before submission.
3. The script, runtime info, and dependency list are posted to the interpreter service.
4. The interpreter returns a JSON payload (`success`, `stdout`, `stderr`, `result`, `error`).
5. `ExecutorResult.data` currently surfaces only the `result` portion of the payload, while `stdout`/`stderr` remain available for future enhancements.

## Configuration Schema

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `runtime.language` | enum | `"python"` | Interpreter runtime; Python is the sole option today. |
| `runtime.version` | string \| `null` | `null` | Optional version hint forwarded to the service. |
| `runtime.dependencies` | list\<string> | `[]` | Optional package requirements. Entries are trimmed; empty strings raise validation errors. |
| `script.kind` | literal `"inline"` | `"inline"` | Script source type (inline only for milestone one). |
| `script.code` | string | — | Python source code executed by the interpreter. |
| `resultVariable` | string \| `null` | `null` | Flow variable populated with the interpreter’s `result` field. |
| `directOutput` | boolean | `false` | If `true`, the interpreter response becomes the flow’s direct output. |
| `timeout` | integer | `0` | Request timeout in seconds; `0` disables the guard. |
| `maxRetries` | integer | `0` | Transport-level retry attempts; `0` means no retries. |

### Interpreter Response Shape

```json
{
  "success": true,
  "error": {},
  "stdout": "Installed 9 packages in 9ms\n<output>...</output>\n",
  "stderr": null,
  "result": {
    "id": 2,
    "name": "Ervin Howell",
    "username": "Antonette"
  }
}
```

- `ExecutorResult.data` equals the inner `result` object.
- `resultVariable` stores the same `result` payload when configured.
- Non-success payloads trigger `ExecutorError` with the interpreter’s best available message (`error.message`, `stderr`, or a fallback string).

## Usage

### Minimal Script
```json
{
  "type": "codeInterpreter",
  "config": {
    "runtime": {"language": "python"},
    "script": {
      "kind": "inline",
      "code": "print('Hello from the interpreter!')"
    }
  }
}
```

### With Dependencies and Downstream LLM
```json
{
  "type": "codeInterpreter",
  "config": {
    "runtime": {
      "language": "python",
      "dependencies": ["requests"]
    },
    "script": {
      "kind": "inline",
      "code": "import requests\nprint(requests.get('https://jsonplaceholder.typicode.com/users/2').json())"
    },
    "resultVariable": "user_payload"
  }
}
```
Follow with an `llmInstruction` step (`instruction: "Summarise {{ $user_payload }} in two sentences."`) for a quick interpreter → LLM handoff. A full example lives in `examples/1_basic_executors/code_interpreter_with_llm.json`.

## Operational Notes

- **Dependency injection**: When `runtime.dependencies` is non-empty and the script lacks a header, the executor prepends:
  ```
  # /// script
  # dependencies = [
  #   "package",
  # ]
  # ///
  ```
  so the interpreter installs packages via uv.
- **Timeouts & retries**: Both default to `0` (disabled). Set non-zero values for production-grade stability.
- **Error handling**: HTTP errors, JSON decoding issues, or `success: false` responses surface as `ExecutorError`.

## Future Enhancements

Planned improvements (not yet implemented):

- **Configurable entrypoint** – Allow scripts to expose a callable (e.g., `def run(**kwargs):`) and invoke only that entrypoint instead of executing the file top-to-bottom. This enables reusing shared helpers while keeping the executed surface area small. The executor would inject runtime arguments based on the step config and treat the function’s return value as `result`.
- **Structured output mapping** – Let authors declare which response fields feed into which flow variables (e.g., map `stdout` to `log_output`, `result` to `processed_data`). This keeps flows tidy when multiple outputs matter but avoids custom glue code in subsequent steps.
- **Environment injection** – Permit a guarded `environment` block that maps variable names to credential values or static strings. Values would be pulled from the credential manager, encrypted in transit, and removed from logs. This unlocks scripts that require API tokens without hardcoding secrets into the script body.
