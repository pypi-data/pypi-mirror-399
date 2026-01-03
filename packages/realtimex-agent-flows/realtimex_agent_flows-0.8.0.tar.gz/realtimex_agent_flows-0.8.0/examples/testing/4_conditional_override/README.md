# Example 4: Testing a Conditional Node's Logic with `override_config`

This example demonstrates how to test the internal logic of a `Conditional` node in isolation, without executing the steps contained within its `truePath` or `falsePath`.

## The Goal

We want to verify that the `Conditional` node correctly evaluates its condition (`user.age > 18`) and chooses the correct path, but we don't want to execute the potentially expensive or unpredictable `apiCall` step inside the `truePath`.

## The Technique: `override_config`

The `manifest.test.json` uses two key features:

1.  **`target`**: The `target` is set to the `id` of the conditional step (`check_user_age`). This tells the test runner to stop execution immediately after this step is complete.
2.  **`override_config`**: The pin for the `check_user_age` step uses `override_config` to temporarily replace the `truePath` and `falsePath` with empty arrays (`[]`).

When the test runs, the `ConditionalExecutor` receives this modified configuration. It evaluates the condition, selects the `truePath`, sees that it's empty, and finishes successfully. The test result will show that the conditional logic worked correctly without ever attempting to run the `apiCall`.
