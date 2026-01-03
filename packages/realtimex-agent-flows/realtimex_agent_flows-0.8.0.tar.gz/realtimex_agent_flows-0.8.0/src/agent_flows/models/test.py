"""Test-related Pydantic models."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from agent_flows.models.execution import ExecutorResult


class TestManifest(BaseModel):
    """Test manifest configuration for flow testing."""

    name: str = Field(..., description="Name of the test scenario")
    target: str | None = Field(None, description="Target step ID to stop execution at")
    initial_variables: dict[str, Any] = Field(
        default_factory=dict, description="Initial variables for the test run"
    )
    pins: list["PinnedResult"] = Field(
        default_factory=list, description="Pinned results for specific steps"
    )

    @model_validator(mode="after")
    def create_pin_dict(self):
        """Create pin lookup dictionary after validation."""
        # Create dictionary for O(1) pin lookup
        self._pin_dict = {pin.step_id: pin for pin in self.pins}
        return self

    def has_pin(self, step_id: str) -> bool:
        """Check if a step has a pinned result.

        Args:
            step_id: Step identifier to check

        Returns:
            True if step has a pinned result
        """
        return step_id in self._pin_dict

    def get_pin(self, step_id: str) -> "PinnedResult | None":
        """Get pinned result for a step.

        Args:
            step_id: Step identifier

        Returns:
            PinnedResult if found, None otherwise
        """
        return self._pin_dict.get(step_id)

    @classmethod
    def from_file(cls, file_path: str) -> "TestManifest":
        """Load test manifest from JSON file.

        Args:
            file_path: Path to test manifest JSON file

        Returns:
            TestManifest instance

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid
        """
        import json
        from pathlib import Path

        manifest_path = Path(file_path)
        if not manifest_path.exists():
            raise FileNotFoundError(f"Test manifest file not found: {file_path}")

        try:
            with open(manifest_path) as f:
                data = json.load(f)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in test manifest: {str(e)}") from e
        except Exception as e:
            raise ValueError(f"Failed to load test manifest: {str(e)}") from e

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TestManifest":
        """Create test manifest from dictionary.

        Args:
            data: Test manifest data as dictionary

        Returns:
            TestManifest instance

        Raises:
            ValueError: If data is invalid
        """
        try:
            return cls(**data)
        except Exception as e:
            raise ValueError(f"Invalid test manifest data: {str(e)}") from e


class PinnedResult(BaseModel):
    """
    A lightweight, predefined result or configuration override for a specific
    step, used for testing.
    """

    step_id: str = Field(..., description="The unique identifier of the step to pin.")
    variables_updated: dict[str, Any] | None = Field(
        None,
        description="A dictionary of variables that the step should produce as output.",
    )
    override_config: dict[str, Any] | None = Field(
        None,
        description="A dictionary to override parts of the step's configuration for this test run.",
    )

    def to_executor_result(self, step_config: dict[str, Any]) -> ExecutorResult:
        """Convert the pinned data into a full ExecutorResult.

        This method uses the original step's configuration to intelligently
        construct a realistic result, correctly handling the primary data output
        and the direct_output flag.

        Args:
            step_config: The interpolated configuration of the step being pinned.

        Returns:
            An ExecutorResult instance that simulates a real execution.
        """
        # Use an empty dict if variables_updated is not provided
        variables = self.variables_updated or {}

        # Determine the primary output data by checking the result variable name
        # in the step's configuration. This makes the pin more robust.
        result_var = step_config.get("resultVariable") or step_config.get("responseVariable")
        inferred_data = variables.get(result_var) if result_var else None

        # Respect the directOutput flag from the original step's config
        direct_output = step_config.get("directOutput", False)

        return ExecutorResult(
            success=True,
            data=inferred_data,
            variables_updated=variables.copy(),
            direct_output=direct_output,
            error=None,
            execution_time=0.01,  # Simulate a small, non-zero execution time
            metadata={"pinned": True},
        )
