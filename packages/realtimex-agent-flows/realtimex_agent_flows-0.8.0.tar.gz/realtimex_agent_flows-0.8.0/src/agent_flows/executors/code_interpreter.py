"""Code Interpreter executor implementation."""

from __future__ import annotations

import asyncio
import json
import sys
import time
import uuid
from typing import Any

import aiohttp
from pydantic import ValidationError

from agent_flows.exceptions import ConfigurationError, ExecutorError
from agent_flows.executors.base import BaseExecutor
from agent_flows.models.execution import ExecutionContext, ExecutorResult
from agent_flows.models.executors.code_interpreter import CodeInterpreterExecutorConfig
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class CodeInterpreterExecutor(BaseExecutor):
    """Executor for executing scripts via the local code interpreter service."""

    DEFAULT_ENDPOINT = "http://127.0.0.1:8004/python-interpreter/run"

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate configuration structure using the Pydantic model."""
        CodeInterpreterExecutorConfig(**config)
        return True

    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Execute code using the interpreter service."""
        start_time = time.time()

        try:
            parsed_config = CodeInterpreterExecutorConfig(**config)
        except ValidationError:
            # Bubble up validation errors for consistent formatting.
            raise
        except Exception as exc:
            raise ConfigurationError(f"Invalid Code Interpreter configuration: {exc}") from exc

        payload = self._build_request_payload(parsed_config, context)

        log.info(
            "Executing code interpreter step",
            language=parsed_config.runtime.language.value,
            version=parsed_config.runtime.version,
            dependency_count=len(parsed_config.runtime.dependencies),
            step_id=context.step_id,
        )

        streaming_handler = getattr(
            getattr(context, "step_execution_service", None),
            "streaming_handler",
            None,
        )
        if streaming_handler:
            streaming_handler.stream_step(
                "Code Interpreter",
                "Terminal",
                "Executing script via Code Interpreter",
                "Executing script via Code Interpreter",
            )

        try:
            response_payload = await self._invoke_interpreter(
                payload=payload,
                timeout=parsed_config.timeout,
                max_retries=parsed_config.maxRetries,
            )
            result_payload = self._parse_response(response_payload)
        except ExecutorError:
            raise
        except Exception as exc:
            raise ExecutorError(f"Code interpreter execution failed: {exc}") from exc

        execution_time = time.time() - start_time

        metadata = {
            "runtime": parsed_config.runtime.language.value,
        }

        step_result = result_payload.get("result")
        stdout = result_payload.get("stdout") or ""
        stderr = result_payload.get("stderr") or ""

        if stdout:
            # Temporary: print to console so multi-line stdout stays readable in logs.
            print(f"Code interpreter stdout: {stdout}")
        if stderr:
            # Temporary: print to console so multi-line stderr stays readable in logs.
            print(f"Code interpreter stderr: {stderr}", file=sys.stderr)

        variables_updated: dict[str, Any] = {}
        if parsed_config.resultVariable:
            variables_updated[parsed_config.resultVariable] = step_result

        result = ExecutorResult(
            success=True,
            data=step_result,
            variables_updated=variables_updated,
            direct_output=parsed_config.directOutput,
            execution_time=execution_time,
            metadata=metadata,
        )

        log.info(
            "Code interpreter step completed",
            step_id=context.step_id,
            execution_time=execution_time,
        )

        return result

    def _build_request_payload(
        self, config: CodeInterpreterExecutorConfig, context: ExecutionContext
    ) -> dict[str, Any]:
        """Construct the request payload for the interpreter service."""
        script_body = config.script.code

        if config.runtime.dependencies and not self._has_dependency_header(script_body):
            script_body = self._inject_dependency_header(script_body, config.runtime.dependencies)

        payload: dict[str, Any] = {
            "language": config.runtime.language.value,
            "script": script_body,
            "run_id": str(uuid.uuid4()),
        }

        if context.variables:
            payload["variables"] = context.variables

        if context.session_id:
            payload["session_id"] = context.session_id

        if context.thread_id:
            payload["thread_id"] = context.thread_id

        if context.workspace_slug:
            payload["workspace_slug"] = context.workspace_slug

        if context.agent_id:
            payload["agent_id"] = context.agent_id

        if config.runtime.version:
            payload["version"] = config.runtime.version

        if config.runtime.dependencies:
            payload["dependencies"] = config.runtime.dependencies

        return payload

    def _has_dependency_header(self, script: str) -> bool:
        """Detect whether the script already declares dependencies."""
        return "# dependencies" in script

    def _inject_dependency_header(self, script: str, dependencies: list[str]) -> str:
        """Inject a uv-compatible dependency header into the script."""
        header_lines = [
            "# /// script",
            "# dependencies = [",
        ]
        header_lines.extend(f'#   "{dep}",' for dep in dependencies)
        header_lines.extend(
            [
                "# ]",
                "# ///",
                "",
            ]
        )

        header = "\n".join(header_lines)
        return f"{header}{script}"

    async def _invoke_interpreter(
        self,
        *,
        payload: dict[str, Any],
        timeout: int,
        max_retries: int,
    ) -> dict[str, Any]:
        """Send the request to the interpreter service with retry handling."""
        attempt = 0
        while True:
            try:
                return await self._send_request(self.DEFAULT_ENDPOINT, payload, timeout)
            except (aiohttp.ClientError, TimeoutError) as exc:
                if attempt >= max_retries:
                    raise ExecutorError(
                        f"Interpreter request failed after {attempt + 1} attempt(s): {exc}"
                    ) from exc

                attempt += 1
                delay = self._retry_delay(attempt)
                log.warning(
                    "Retrying interpreter request",
                    attempt=attempt,
                    delay=delay,
                    error=str(exc),
                )
                await asyncio.sleep(delay)

    async def _send_request(
        self,
        endpoint: str,
        payload: dict[str, Any],
        timeout: int,
    ) -> dict[str, Any]:
        """Perform a single interpreter HTTP request."""
        client_timeout = aiohttp.ClientTimeout(total=None if timeout == 0 else timeout)

        async with (
            aiohttp.ClientSession(timeout=client_timeout) as session,
            session.post(endpoint, json=payload) as response,
        ):
            response_text = await response.text()

            if response.status >= 400:
                raise ExecutorError(f"Interpreter returned HTTP {response.status}: {response_text}")

            try:
                return json.loads(response_text)
            except json.JSONDecodeError as exc:
                raise ExecutorError("Interpreter returned invalid JSON response") from exc

    def _retry_delay(self, attempt: int) -> float:
        """Compute exponential backoff delay capped at five seconds."""
        return float(min(2 ** (attempt - 1), 5))

    def _parse_response(
        self,
        payload: Any,
    ) -> dict[str, Any]:
        """Validate interpreter response and shape result data."""
        if not isinstance(payload, dict):
            raise ExecutorError("Interpreter response must be a JSON object")

        success = payload.get("success")
        if success is not True:
            error_detail = payload.get("error")
            message: str | None = None

            if isinstance(error_detail, dict) and error_detail:
                message = error_detail.get("message") or json.dumps(error_detail)
            elif isinstance(error_detail, str) and error_detail.strip():
                message = error_detail.strip()
            elif payload.get("stderr"):
                message = str(payload["stderr"])

            if not message:
                message = "Interpreter reported failure"

            raise ExecutorError(f"Interpreter execution failed: {message}")

        stdout = payload.get("stdout") or ""
        result_data: dict[str, Any] = {
            "stdout": stdout,
            "stderr": payload.get("stderr"),
            "result": payload.get("result"),
            "error": payload.get("error"),
        }

        return result_data
