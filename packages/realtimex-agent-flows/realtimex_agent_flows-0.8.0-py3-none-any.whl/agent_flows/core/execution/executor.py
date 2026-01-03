"""Main FlowExecutor class for orchestrating flow execution."""

from datetime import UTC, datetime
from typing import Any

from pydantic import ValidationError

from agent_flows.core.execution import (
    ExecutionResult,
    ExecutorRegistry,
    FlowRunner,
    StepExecutionService,
)
from agent_flows.core.flows import FlowLoader, FlowRegistry
from agent_flows.core.resources import (
    CredentialManager,
    MCPSessionPool,
    VariableInterpolator,
    VariableManager,
)
from agent_flows.exceptions import (
    FlowExecutionError,
)
from agent_flows.models.config import AgentFlowsConfig
from agent_flows.models.execution import (
    ExecutionContext,
    ExecutionError,
    FlowResult,
    FlowResultData,
    FlowResultType,
    TraceEntry,
)
from agent_flows.models.flow import FlowConfig
from agent_flows.models.test import TestManifest
from agent_flows.streaming import StreamingHandler
from agent_flows.utils.config import load_config
from agent_flows.utils.logging import (
    get_logger,
    setup_logging,
)
from agent_flows.utils.test_utils import parse_test_manifest
from agent_flows.utils.validation import (
    StepValidationResult,
    format_validation_errors,
)

log = get_logger(__name__)


class FlowExecutor:
    """Main class for executing Agent Flows."""

    def __init__(
        self,
        config: AgentFlowsConfig | None = None,
        session_id: str | None = None,
        workspace_slug: str | None = None,
        thread_id: str | None = None,
        agent_id: str | None = None,
    ) -> None:
        """Initialize FlowExecutor.

        Args:
            config: AgentFlowsConfig instance with all configuration
            session_id: Optional identifier used for streaming sessions

        Note:
            If config is not provided, configuration is loaded from environment variables.
        """
        # Load configuration with priority: config > environment variables
        self.config = config if config is not None else load_config()

        # Setup logging from configuration
        setup_logging(level=self.config.logging.level, json_format=self.config.logging.json_format)

        # Session ID for streaming context
        self.session_id = session_id

        # Workspace Slug
        self.workspace_slug = workspace_slug

        # Session ID for streaming context
        self.thread_id = thread_id

        # Agent ID for context
        self.agent_id = agent_id

        # Initialize core components
        self.flow_registry = FlowRegistry(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            flow_ttl=self.config.cache_ttl,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries,
        )
        self.flow_loader = FlowLoader(self.flow_registry)
        self.executor_registry = ExecutorRegistry()
        self.variable_interpolator = VariableInterpolator()
        self.credential_manager = CredentialManager(self.config)
        self.variable_manager = VariableManager(self.config)

        # Initialize streaming handler
        self.streaming_handler = StreamingHandler(session_id=session_id)

        # Initialize step execution service
        self.step_execution_service = StepExecutionService(
            self.executor_registry,
            self.streaming_handler,
            credential_manager=self.credential_manager,
        )

        # Execution state
        self._closed = False

    async def execute_flow(
        self,
        flow_source: FlowConfig | str,
        variables: dict[str, Any] | None = None,
        test_manifest: TestManifest | None = None,
        include_trace: bool = False,
    ) -> FlowResult:
        """Execute a flow from various sources.

        Args:
            flow_source: FlowConfig object, UUID string, or file path
            variables: Initial variables for the flow
            test_manifest: Optional test manifest for test mode execution
            include_trace: Whether to include step-by-step execution trace

        Returns:
            FlowResult with execution results

        Raises:
            FlowExecutionError: If flow execution fails
        """
        if self._closed:
            raise FlowExecutionError("FlowExecutor has been closed")

        try:
            # Resolve flow configuration
            flow_config = await self.flow_loader.load(flow_source)
            flow_id = flow_config.uuid

            # Initialize variables and execution context
            flow_variables = await self.variable_manager.initialize_variables(
                flow_config, variables
            )

            # Prepare trace log if requested
            trace_log: list[TraceEntry] | None = [] if include_trace else None

            # Create MCP session pool for persistent connections
            mcp_session_pool = MCPSessionPool(flow_id)

            execution_context = ExecutionContext(
                variables=flow_variables,
                flow_id=flow_id,
                step_index=0,
                step_id="",
                config=self.config,
                step_execution_service=self.step_execution_service,
                test_manifest=test_manifest,
                trace_log=trace_log,
                mcp_session_pool=mcp_session_pool,
                session_id=self.session_id,
                thread_id=self.thread_id,
                workspace_slug=self.workspace_slug,
                agent_id=self.agent_id,
            )

            # Delegate to Flow Runner for execution
            flow_runner = FlowRunner(self.step_execution_service, self.streaming_handler)
            try:
                execution_result = await flow_runner.run(
                    flow_config=flow_config,
                    execution_context=execution_context,
                    test_manifest=test_manifest,
                )

                # Convert ExecutionResult to FlowResult/TestResult
                return self._build_final_result(execution_result, test_manifest, flow_id)
            finally:
                # Always clean up MCP sessions
                await mcp_session_pool.close_all()

        except Exception as e:
            # Handle all execution failures with unified error response
            return self._build_error_result(
                error=e,
                flow_source=flow_source,
                variables=variables,
                test_manifest=test_manifest,
            )

    async def test(
        self,
        flow_source: FlowConfig | str,
        test_manifest: str | dict[str, Any] | TestManifest | None = None,
        include_trace: bool = False,
    ) -> FlowResult:
        """Execute a flow in test mode asynchronously.

        Args:
            flow_source: FlowConfig object, UUID string, or file path for the flow under test
            test_manifest: Test manifest as file path, dict, TestManifest instance, or None for full flow execution
            include_trace: Whether to include step-by-step execution trace

        Returns:
            FlowResult with results of the test execution

        Raises:
            FileNotFoundError: If test manifest file path doesn't exist
            ValueError: If test manifest data is invalid
            FlowExecutionError: If flow execution fails
        """
        parsed_manifest = parse_test_manifest(test_manifest)

        if parsed_manifest:
            log.info(
                "Starting test execution with manifest",
                test_name=parsed_manifest.name,
                target_step=parsed_manifest.target,
                pinned_steps=len(parsed_manifest.pins),
            )
            initial_variables = parsed_manifest.initial_variables
        else:
            log.info("Starting test execution without manifest (full flow)")
            initial_variables = None

        return await self.execute_flow(
            flow_source=flow_source,
            variables=initial_variables,
            test_manifest=parsed_manifest,
            include_trace=include_trace,
        )

    async def list_flows(self) -> list[FlowConfig]:
        """List all available flows with full configurations."""
        if self._closed:
            raise FlowExecutionError("FlowExecutor has been closed")

        return await self.flow_registry.list_flows()

    async def get_flow_info(self, flow_id: str) -> FlowConfig:
        """Get detailed information about a flow.

        Args:
            flow_id: UUID of the flow

        Returns:
            FlowConfig object with complete flow information
        """
        if self._closed:
            raise FlowExecutionError("FlowExecutor has been closed")

        return await self.flow_registry.get_flow(flow_id)

    async def validate_flow(self, flow_source: FlowConfig | str) -> dict[str, Any]:
        """Validate a flow configuration from any supported source.

        Args:
            flow_source: FlowConfig object, UUID string, or file path to validate

        Returns:
            Dictionary with validation results in the format:
            {
                "valid": bool,
                "step_validation_summary": [
                    {
                        "step_id": str,
                        "step_type": str,
                        "step_index": int,
                        "valid": bool,
                        "messages": [str, ...]
                    },
                    ...
                ]
            }

        Raises:
            FlowExecutionError: If the executor is closed.
        """
        if self._closed:
            raise FlowExecutionError("FlowExecutor has been closed")

        try:
            flow_config = await self.flow_loader.load(flow_source)
            return self._validate_flow_config(flow_config)
        except Exception as e:
            # Return error for unexpected validation failures
            return {
                "valid": False,
                "step_validation_summary": [
                    {
                        "step_id": "unknown",
                        "step_type": "unknown",
                        "valid": False,
                        "messages": [f"An unexpected error occurred during validation: {str(e)}"],
                    }
                ],
            }

    async def close(self) -> None:
        """Close the executor and cleanup resources."""
        if not self._closed:
            log.info("Closing FlowExecutor")
            if hasattr(self.flow_registry, "close"):
                await self.flow_registry.close()
            if hasattr(self.credential_manager, "close"):
                await self.credential_manager.close()
            if hasattr(self.variable_manager, "close"):
                await self.variable_manager.close()
            self._closed = True

    async def __aenter__(self) -> "FlowExecutor":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def _validate_flow_config(self, flow_config: FlowConfig) -> dict[str, Any]:
        """Perform validation on a given FlowConfig object."""
        step_results = []
        overall_valid = True
        seen_flow_variables = False
        seen_finish = False

        # Validate each step
        for step in flow_config.steps:
            step_result = StepValidationResult(step.id, step.type)

            try:
                # Legacy/metadata-only START step: allow passthrough without validation
                if step.type.lower() == "start":
                    step_results.append(step_result.to_dict())
                    continue

                if step.type == "flow_variables":
                    if seen_flow_variables:
                        step_result.add_error("Only one flow_variables step is allowed")
                    seen_flow_variables = True

                if step.type == "finish":
                    if seen_finish:
                        step_result.add_error("Only one finish step is allowed")
                    seen_finish = True

                # Check if executor exists
                if not self.executor_registry.is_registered(step.type):
                    step_result.add_error(f"Unknown step type '{step.type}'")
                else:
                    # Validate step configuration using the executor
                    try:
                        self.executor_registry.validate_step_config(step.type, step.config)
                    except ValidationError as e:
                        # Use Pydantic's error details directly with minimal formatting
                        error_messages = format_validation_errors(e, step.type)
                        step_result.add_errors(error_messages)
                    except Exception as e:
                        # Handle other validation errors
                        step_result.add_error(str(e))

            except Exception as e:
                step_result.add_error(f"Unexpected validation error: {str(e)}")

            if not step_result.valid:
                overall_valid = False

            step_results.append(step_result.to_dict())

        return {"valid": overall_valid, "step_validation_summary": step_results}

    def _build_final_result(
        self,
        execution_result: ExecutionResult,
        test_manifest: TestManifest | None,
        flow_id: str,
    ) -> FlowResult:
        """Convert ExecutionResult to FlowResult.

        Args:
            execution_result: Result from FlowRunner execution
            test_manifest: Optional test manifest for test mode
            flow_id: Flow identifier

        Returns:
            FlowResult with execution results
        """
        # Determine result type and data based on execution outcome
        target_step_id = None
        target_step_type = None

        if not execution_result.success:
            result_type = FlowResultType.ERROR
            primary_error = execution_result.errors[0] if execution_result.errors else None
            result_data = self._format_execution_error(primary_error)
        elif execution_result.target_step_result is not None:
            result_type = FlowResultType.HALTED_BY_TARGET
            result_data = execution_result.target_step_result.data
            # Populate target fields when test mode halted at target
            if test_manifest:
                target_step_id = execution_result.target_step_result.step_id
                target_step_type = execution_result.target_step_result.step_type
        elif execution_result.direct_output is not None:
            result_type = FlowResultType.DIRECT_OUTPUT
            result_data = execution_result.direct_output
        else:
            result_type = FlowResultType.COMPLETED
            result_data = execution_result.final_variables

        # Extract flow_as_output from finish metadata if present
        flow_as_output = False

        if execution_result.finish_metadata:
            flow_as_output = execution_result.finish_metadata.get("flow_as_output", False)

        return FlowResult(
            flow_id=flow_id,
            success=execution_result.success,
            execution_time=execution_result.execution_time,
            result=FlowResultData(
                type=result_type,
                data=result_data,
                target_step_id=target_step_id,
                target_step_type=target_step_type,
            ),
            errors=execution_result.errors,
            trace=execution_result.trace,
            flow_as_output=flow_as_output,
        )

    def _build_error_result(
        self,
        error: Exception,
        flow_source: FlowConfig | str,
        variables: dict[str, Any] | None,
        test_manifest: TestManifest | None,
    ) -> FlowResult:
        """Build error result for failed execution.

        Args:
            error: The exception that occurred
            flow_source: Original flow source for fallback ID
            variables: Original variables for error context
            test_manifest: Optional test manifest

        Returns:
            FlowResult with error information
        """
        # Determine flow ID for error reporting
        if isinstance(flow_source, FlowConfig):
            flow_id = flow_source.uuid
        elif isinstance(flow_source, str):
            flow_id = flow_source
        else:
            flow_id = "unknown"

        # Log the error
        log.error("Flow execution failed", flow_id=flow_id, error=str(error), exc_info=True)

        # Emit streaming error event
        self.streaming_handler.flow_error(str(error))

        # Create error result
        execution_errors = [
            ExecutionError(
                message=str(error),
                step_id=None,
                step_index=None,
                step_type=None,
                error_type=type(error).__name__,
                context_variables=variables,
                timestamp=datetime.now(UTC),
            )
        ]

        return FlowResult(
            flow_id=flow_id,
            success=False,
            execution_time=0.0,
            result=FlowResultData(
                type=FlowResultType.ERROR, data=self._format_execution_error(execution_errors[0])
            ),
            errors=execution_errors,
            trace=None,
        )

    @staticmethod
    def _format_execution_error(error: ExecutionError | None) -> dict[str, Any]:
        """Create a frontend-friendly error payload from an ExecutionError."""
        if error is None:
            return {"message": "Flow execution failed", "step_id": ""}

        payload: dict[str, Any] = {
            "message": error.message,
            "step_id": error.step_id or "",
        }

        return payload
