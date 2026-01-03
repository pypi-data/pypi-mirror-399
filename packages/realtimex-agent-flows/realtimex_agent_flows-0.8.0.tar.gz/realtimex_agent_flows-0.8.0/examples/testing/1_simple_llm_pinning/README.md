# Test Example: Simple LLM Pinning

This example demonstrates the core feature of the Agent Flows testing framework: **pinning** the result of a specific step to test a flow's logic without incurring costs or relying on external services.

Here, we test a simple flow that contains an LLM instruction step, but we will use a "pinned" result for the LLM step instead of making a real API call.

## Files in this Directory

- **`flow.json`**: A simple two-step flow containing a `start` step and an `llmInstruction` step.
- **`manifest.test.json`**: The test manifest that defines the test scenario. It provides initial variables and, crucially, a `pins` array that contains the predefined result for the `llm_step`.

## How to Run the Test

You can run this test using the following Python script. This script loads the flow, executes it against the test manifest, and prints the results.

```python
#!/usr/bin/env python3
"""Demo script to demonstrate the test pinning mechanism."""

import os
from agent_flows import FlowExecutor

def main():
    """Demonstrate the test mechanism."""
    print("=== Agent Flows Test Mechanism Demo ===\n")

    # The path to this example directory
    example_dir = os.path.dirname(__file__)
    flow_file_path = os.path.join(example_dir, "flow.json")
    manifest_file_path = os.path.join(example_dir, "manifest.test.json")

    # Create executor from the test flow
    # Note: No API keys are needed because the LLM step will be pinned.
    executor = FlowExecutor.from_file(
        flow_file=flow_file_path,
        log_level="INFO",
        log_json_format=False,
    )

    print(f"1. Testing flow '{os.path.basename(flow_file_path)}' with manifest '{os.path.basename(manifest_file_path)}'...")
    try:
        # Run the test using the manifest
        result = executor.test(manifest_file_path)

        print("\n✅ Test completed successfully!")
        print(f"   Success: {result.success}")
        print(f"   Steps executed: {result.steps_executed}")
        print(f"   Execution time: {result.execution_time:.3f}s")
        
        # Verify that the pinned result was used
        if "llm_response" in result.variables:
            print("\n   LLM Response (from pinned result):")
            print(f"   -> '{result.variables['llm_response'][:100]}...'")

            # Check if the response matches the pinned data
            from agent_flows.models import TestManifest
            manifest = TestManifest.from_file(manifest_file_path)
            pinned_vars = manifest.get_pin("llm_step").variables_updated
            pinned_data = pinned_vars.get("llm_response")
            assert result.variables['llm_response'] == pinned_data
            print("\n   ✅ Assertion passed: The output matches the pinned result.")


    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()

```

## Expected Output

When you run the script, you will see the following output. Notice that the LLM response comes directly from the pinned data in `manifest.test.json`, not from a live API call.

```
=== Agent Flows Test Mechanism Demo ===

1. Testing flow 'flow.json' with manifest 'manifest.test.json'...

✅ Test completed successfully!
   Success: True
   Steps executed: 2
   Execution time: 0.001s

   LLM Response (from pinned result):
   -> 'The capital of France is Paris. It is located in the north-central part of the country and serves as...'

   ✅ Assertion passed: The output matches the pinned result.

=== Demo Complete ===
```
