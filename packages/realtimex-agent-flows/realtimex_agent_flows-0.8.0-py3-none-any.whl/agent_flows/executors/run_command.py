"""Run Command executor implementation."""

from __future__ import annotations

import asyncio
import json
import os
import re
import time
from typing import Any

from pydantic import ValidationError

from agent_flows.exceptions import ConfigurationError, ExecutorError
from agent_flows.executors.base import BaseExecutor
from agent_flows.models.execution import ExecutionContext, ExecutorResult
from agent_flows.models.executors.run_command import RunCommandExecutorConfig
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class RunCommandExecutor(BaseExecutor):
    """Executor for running CLI commands via subprocess.

    Commands are executed without a shell (safer, more predictable).
    For shell features, use: command="sh", args=["-c", "your | shell | command"]
    """

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate configuration structure using the Pydantic model."""
        RunCommandExecutorConfig(**config)
        return True

    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Execute a CLI command."""
        start_time = time.time()

        try:
            parsed_config = RunCommandExecutorConfig(**config)
        except ValidationError:
            raise
        except Exception as exc:
            raise ConfigurationError(f"Invalid Run Command configuration: {exc}") from exc

        log.info(
            "Executing run command step",
            command=parsed_config.command,
            args=parsed_config.args,
            cwd=parsed_config.cwd,
            step_id=context.step_id,
        )

        # Stream step progress if handler is available
        streaming_handler = getattr(
            getattr(context, "step_execution_service", None),
            "streaming_handler",
            None,
        )
        if streaming_handler:
            streaming_handler.stream_step(
                "Run Command",
                "Terminal",
                f"Executing: {parsed_config.command}",
                f"Running command: {parsed_config.command}",
            )

        try:
            exit_code, stdout, stderr = await self._run_command(
                command=parsed_config.command,
                args=parsed_config.args,
                cwd=parsed_config.cwd,
                env=parsed_config.env,
                timeout=parsed_config.timeout,
            )
        except TimeoutError:
            raise ExecutorError(
                f"Command timed out after {parsed_config.timeout} seconds"
            ) from None
        except Exception as exc:
            raise ExecutorError(f"Command execution failed: {exc}") from exc

        execution_time = time.time() - start_time

        # Determine success based on exit code
        success = exit_code == 0

        if not success:
            raise ExecutorError(f"Command exited with code {exit_code}: {stderr or stdout}")

        # Extract result using <output>...</output> pattern or fallback to stdout
        result = self._extract_result(stdout)

        # Build metadata with verbose output
        metadata: dict[str, Any] = {
            "exitCode": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "command": parsed_config.command,
            "args": parsed_config.args,
        }

        # Update variables if resultVariable is set
        variables_updated: dict[str, Any] = {}
        if parsed_config.resultVariable:
            variables_updated[parsed_config.resultVariable] = result

        log.info(
            "Run command step completed",
            step_id=context.step_id,
            exit_code=exit_code,
            execution_time=execution_time,
        )

        return ExecutorResult(
            success=True,
            data=result,
            variables_updated=variables_updated,
            direct_output=parsed_config.directOutput,
            execution_time=execution_time,
            metadata=metadata,
        )

    async def _run_command(
        self,
        *,
        command: str,
        args: list[str],
        cwd: str | None,
        env: dict[str, str],
        timeout: int,
    ) -> tuple[int, str, str]:
        """Execute the command via subprocess.

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        # Merge environment variables with current environment
        merged_env = os.environ.copy()
        merged_env.update(env)

        log.debug(
            "Spawning subprocess",
            command=command,
            args=args,
            cwd=cwd,
        )

        process = await asyncio.create_subprocess_exec(
            command,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=merged_env,
        )

        # Apply timeout if specified
        if timeout > 0:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
        else:
            stdout_bytes, stderr_bytes = await process.communicate()

        stdout = stdout_bytes.decode("utf-8", errors="replace") if stdout_bytes else ""
        stderr = stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else ""

        return process.returncode or 0, stdout, stderr

    def _extract_result(self, stdout: str) -> Any:
        """Extract result from stdout using <output>...</output> pattern.

        If the pattern is found, attempts to parse the content as JSON.
        Falls back to the full stdout if no pattern is found.

        Args:
            stdout: Standard output from the command

        Returns:
            Extracted result (parsed JSON if possible, otherwise string)
        """
        # Look for <output>...</output> pattern
        match = re.search(r"<output>(.*?)</output>", stdout, re.DOTALL)
        if match:
            result = match.group(1).strip()
            # Try to parse as JSON
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return result

        # Fallback: use trimmed stdout
        stripped = stdout.strip()
        return stripped if stripped else None
