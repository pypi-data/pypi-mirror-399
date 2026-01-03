# Test Example: Simple Loop Pinning

This example provides a clear and focused demonstration of **deep pinning** within a `loop` step. 

Deep pinning is the ability to replace the result of a step that is *nested inside* a composite step (like a loop). This allows you to test the loop's logic (e.g., that it iterates correctly) without running the actual expensive or external-facing steps inside it.

## Files in this Directory

- **`flow.json`**: A minimal flow that contains a `loop` step. The loop is designed to iterate over a list of users and contains a nested `llmInstruction` step to look up user profiles.
- **`manifest.test.json`**: The test manifest that pins the result for the nested `expensive_user_lookup` step. Every time the loop tries to run this step, the testing framework will return this pinned result instead of making an LLM call.

## How to Run the Test

You can run this test using the following Python script. The script loads the flow and manifest, runs the test, and validates that the loop iterated the correct number of times using the pinned data.

```python
#!/usr/bin/env python3
"""Demo script to validate deep pinning in a simple loop."""

import os
from agent_flows import FlowExecutor

def main():
    """Test deep pinning with a simple, clean example."""
    print("=== Simple Loop Pinning Demo ===\n")

    example_dir = os.path.dirname(__file__)
    flow_file_path = os.path.join(example_dir, "flow.json")
    manifest_file_path = os.path.join(example_dir, "manifest.test.json")

    executor = FlowExecutor.from_file(
        flow_file=flow_file_path,
        log_level="INFO",
        log_json_format=False,
    )

    print("1. Testing deep pinning in a loop...")
    try:
        result = executor.test(manifest_file_path)

        print("\n✅ Test Completed!")
        print(f"   Success: {result.success}")

        # --- Validation ---
        print("\n2. Validating behavior...")
        profiles = result.variables.get("all_user_profiles", [])
        
        # The manifest provides 2 users, so the loop should run twice.
        if len(profiles) == 2:
            print(f"   ✅ Loop ran for 2 items as defined in the manifest.")
        else:
            print(f"   ❌ Loop ran {len(profiles)} times, expected 2.")

        # Check that the data from the pinned step was used in the results.
        first_profile_data = profiles[0].get("user_profile", {})
        if first_profile_data.get("user_id") == "mocked_user_123":
            print(f"   ✅ Pinned result was correctly used in the loop output.")
        else:
            print("   ❌ Loop output does not contain the pinned data.")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()

```

## Expected Output

```
=== Simple Loop Pinning Demo ===

1. Testing deep pinning in a loop...

✅ Test Completed!
   Success: True

2. Validating behavior...
   ✅ Loop ran for 2 items as defined in the manifest.
   ✅ Pinned result was correctly used in the loop output.

=== Demo Complete ===
```
