# Test Example: Composite Node Pinning

This example demonstrates a more advanced testing scenario: **deep pinning** for composite nodes like `loop` and `conditional`.

Deep pinning allows you to pin the results of steps that are *nested inside* another step. This is powerful for testing complex workflows where you want to isolate the logic of the parent composite node (e.g., the loop or conditional itself) without executing the expensive nested steps (e.g., API calls or LLM instructions inside a loop).

## Files in this Directory

- **`flow.json`**: A flow containing a `loop` step and a `conditional` step. Both of these composite nodes contain nested `llmInstruction` steps.
- **`manifest.test.json`**: The test manifest that pins the results for the nested steps (`expensive_processing` inside the loop, and `expensive_api_call` inside the conditional). This allows the test to run without any real LLM calls.

## How to Run the Test

The Python script below loads the flow and its test manifest. It then executes the test, demonstrating that the `truePath` of the conditional is correctly taken and that the final `analysis_result` variable is present.

```python
#!/usr/bin/env python3
"""Demo script to demonstrate composite node pinning."""

import os
from agent_flows import FlowExecutor

def main():
    """Demonstrate the test mechanism for composite nodes."""
    print("=== Composite Node Pinning Demo ===\n")

    example_dir = os.path.dirname(__file__)
    flow_file_path = os.path.join(example_dir, "flow.json")
    manifest_file_path = os.path.join(example_dir, "manifest.test.json")

    executor = FlowExecutor.from_file(
        flow_file=flow_file_path,
        log_level="INFO",
        log_json_format=False,
    )

    print(f"1. Testing flow with deep pinning from manifest '{os.path.basename(manifest_file_path)}'...")
    try:
        result = executor.test(manifest_file_path)

        print("\n✅ Test completed successfully!")
        print(f"   Success: {result.success}")
        print(f"   Steps executed: {result.steps_executed}")
        print(f"   Final variables: {list(result.variables.keys())}")

        # --- Validation ---
        print("\n2. Validating behavior...")
        expected_vars = ["items", "condition_flag", "loop_results", "analysis_result"]
        missing_vars = [var for var in expected_vars if var not in result.variables]

        if not missing_vars:
            print("   ✅ All expected variables are present.")
            print(f"   ✅ Conditional took the correct path and created 'analysis_result'.")
        else:
            print(f"   ❌ Missing expected variables: {missing_vars}")

        # Check loop results
        loop_results = result.variables.get("loop_results", [])
        if len(loop_results) == 2:
            print(f"   ✅ Loop ran for 2 items as defined in the manifest.")
        else:
            print(f"   ❌ Loop ran {len(loop_results)} times, expected 2.")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()

```

## Expected Output

With the corrected `variable` syntax (`{{ $condition_flag }}`), the conditional now evaluates to `True`, the `truePath` is executed, and the `analysis_result` variable is created from the pinned result.

```
=== Composite Node Pinning Demo ===

1. Testing flow with deep pinning from manifest 'manifest.test.json'...

✅ Test completed successfully!
   Success: True
   Steps executed: 3
   Final variables: ['items', 'condition_flag', 'current_item', 'item_index', 'processed_item', 'loop_results', 'analysis_result']

2. Validating behavior...
   ✅ All expected variables are present.
   ✅ Conditional took the correct path and created 'analysis_result'.
   ✅ Loop ran for 2 items as defined in the manifest.

=== Demo Complete ===
```
