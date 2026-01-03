# Agent Flows Examples

This directory contains a curated collection of Agent Flow examples, organized to help users (developers, humans, and AI agents) easily understand and utilize the capabilities of the Agent Flows Python package.

## Organization

Examples are grouped into thematic subdirectories:

-   **`1_basic_executors/`**: Contains simple, isolated examples for each core executor type. Ideal for understanding the fundamental usage of individual executors.
-   **`2_advanced_web_scraping/`**: Showcases advanced use cases and configurations for the Web Scraping executor, demonstrating its versatility.
-   **`3_workflows/`**: Features complex, multi-step workflows that combine various executors to solve real-world problems or demonstrate advanced flow logic.
-   **`variables/`**: Stores standalone variable definition files that can be used as inputs for various flows.

## How to Use These Examples

Each example is a JSON file representing an Agent Flow. You can run these flows using the `agent-flows` CLI or programmatically within your Python applications.

### Running Examples via CLI

To run an example, use the `agent-flows run` command followed by the path to the flow file. For example:

```bash
# Run a basic API Call example
agent-flows run examples/1_basic_executors/api_call.json

# Run a complex workflow
agent-flows run examples/3_workflows/2_breaking_news_to_linkedin/flow.json

# Run a workflow with a separate variables file
agent-flows run examples/3_workflows/2_breaking_news_to_linkedin/flow.json \
  --variables-file examples/3_workflows/2_breaking_news_to_linkedin/variables.json
```

### Running Examples Programmatically

You can load and execute these flows within your Python code:

```python
import asyncio
from agent_flows import FlowExecutor

async def main():
    executor = FlowExecutor.from_file(
        flow_file="examples/1_basic_executors/start.json"
    )
    result = await executor.execute_flow()
    print(f"Flow executed successfully: {result.success}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Contributing New Examples

When adding new examples, please follow the established organization and naming conventions. Ensure your example is well-commented and demonstrates a clear use case.

```