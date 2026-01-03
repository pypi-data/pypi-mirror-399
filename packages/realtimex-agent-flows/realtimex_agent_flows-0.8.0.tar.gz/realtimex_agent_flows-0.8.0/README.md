# Agent Flows Python Package

A powerful Python library for executing Agent Flows - visual, no-code workflows that integrate seamlessly into Python applications.

## Features

- **Multiple Executors**: Built-in support for 8 different executor types (API calls, LLM instructions, MCP servers, etc.)
- **Flow Initialization**: Use the `flow_variables` step type (`start` remains as a deprecated alias) to seed runtime data consistently across flows.
- **MCP Integration**: Native support for Model Context Protocol (MCP) servers and tools
- **Flexible Usage**: Run flows from RealTimeX instances or local JSON files
- **Simple API**: Easy-to-use methods with explicit parameters
- **CLI Interface**: Command-line tools with `uvx` support (no installation required)
- **Async & Sync**: Both async/await and synchronous execution options
- **Type Safety**: Full type hints and Pydantic validation
- **JSON Configuration**: Simple, consistent configuration format
- **Testing Framework**: Deep pinning support for testing flows without API costs, including composite nodes (loops, conditionals)

## Quick Start

### Installation

```bash
# Install via pip
pip install agent-flows

# Or use with uvx for one-time execution (no installation required)
uvx agent-flows execute --flow-id <uuid> --api-key <key> --base-url <url>
```

### Configuration

Configure using environment variables:

```bash
export AGENT_FLOWS_API_KEY="your-realtimex-api-key"
export AGENT_FLOWS_BASE_URL="https://your-realtimex-instance.com"
export LITELLM_API_KEY="your-llm-api-key"

# For MCP server integration
export MCP_ACI_API_KEY="your-aci-api-key"
export MCP_ACI_LINKED_ACCOUNT_OWNER_ID="your-linked-account-owner-id"
```

## Usage

### 1. Execute Flows from RealTimeX

```python
import asyncio
from agent_flows import FlowExecutor, AgentFlowsConfig, LiteLLMConfig

# Option 1: Use environment variables (recommended)
executor = FlowExecutor()

# Option 2: Create explicit configuration
system_config = AgentFlowsConfig(
    api_key="your-realtimex-api-key",
    base_url="https://your-realtimex-instance.com",
    litellm=LiteLLMConfig(
        api_key="your-llm-api-key",
        api_base="https://api.openai.com/v1"
    )
)
executor = FlowExecutor(config=system_config)

# Execute flow with explicit parameters
result = await executor.execute_flow(
    flow_id="550e8400-e29b-41d4-a716-446655440000",
    variables={"input_param": "value", "max_results": 10}
)

print(f"Success: {result.success}")
print(f"Steps executed: {result.steps_executed}")
print(f"Execution time: {result.execution_time:.2f}s")
```

### 2. Execute Local Flow Files

```python
from agent_flows import FlowExecutor

# Create executor from local flow file (uses environment variables for LLM/API config)
executor = FlowExecutor.from_file(
    flow_file="examples/1_basic_executors/start.json"
)

# Execute with explicit parameters
result = await executor.execute_flow(
    variables={"name": "World", "greeting": "Hello"}
)

print(f"Local flow result: {result.success}")
```

### 3. Synchronous Execution (No async/await)

```python
from agent_flows import FlowExecutor

# Create executor (uses environment variables)
executor = FlowExecutor.from_file(flow_file="examples/simple_flow.json")

# Run synchronously with explicit parameters
result = executor.run(
    variables={"name": "World"}
)

print(f"Success: {result.success}")
```

### 4. Configuration Options

```python
from agent_flows import FlowExecutor, AgentFlowsConfig

# Option 1: From environment variables (recommended)
executor = FlowExecutor()  # Uses AGENT_FLOWS_* env vars

# Option 2: Explicit configuration
system_config = AgentFlowsConfig(
    api_key="your-key",
    base_url="https://your-instance.com"
)
executor = FlowExecutor(config=system_config)

# Option 3: From flow dictionary
flow_dict = {"uuid": "123", "name": "Test", "steps": [...]}
executor = FlowExecutor.from_dict(flow_dict=flow_dict)
```

### CLI Usage

#### Execute flows from RealTimeX

```bash
# Execute with environment variables (recommended)
agent-flows execute \
  --flow-id "550e8400-e29b-41d4-a716-446655440000"

# Execute with inline config
agent-flows execute \
  --flow-id "550e8400-e29b-41d4-a716-446655440000" \
  --config '{"api_key":"key","base_url":"url","litellm":{"api_key":"llm-key"}}'

# Execute with variables
agent-flows execute \
  --flow-id "550e8400-e29b-41d4-a716-446655440000" \
  --variables '{"input_text":"Hello World","max_results":10}'
```

#### Execute local flow files

```bash
# Run a local flow file
agent-flows run examples/1_basic_executors/start.json

# Run with variables (JSON string)
agent-flows run examples/3_workflows/2_breaking_news_to_linkedin/flow.json \
  --variables '{"name":"John","age":30}'

# Run with variables from file
agent-flows run examples/3_workflows/2_breaking_news_to_linkedin/flow.json \
  --variables-file examples/3_workflows/2_breaking_news_to_linkedin/variables.json

# Run with explicit config for LLM settings
agent-flows run examples/3_workflows/2_breaking_news_to_linkedin/flow.json \
  --config '{"litellm":{"api_key":"your-llm-key"}}'
```

#### Using uvx (no installation required)

```bash
# Execute a flow with uvx
uvx agent-flows execute \
  --flow-id "550e8400-e29b-41d4-a716-446655440000" \
  --config '{"api_key":"key","base_url":"url","litellm":{"api_key":"llm-key"}}'

# Run a local flow with uvx
uvx agent-flows run examples/1_basic_executors/start.json \
  --variables '{"greeting":"Hello from uvx!"}'
```

## Supported Flow Types

The package includes **8 built-in executors**:

- **Flow Variables**: Variable initialization and flow setup
- **API Call**: HTTP requests with full REST API support and retry logic
- **LLM Instruction**: Multi-provider LLM integration (OpenAI, Anthropic, etc.)
- **Web Scraping**: Content extraction with CSS selectors and auto-summarization
- **Conditional**: Branching logic with multiple comparison operators
- **Switch**: Multi-case routing based on variable values
- **Loop**: Iterative execution with for/while/forEach support and clean output format
- **MCP Server Action**: Execute actions on Model Context Protocol (MCP) servers

For detailed documentation on each executor, see [docs/executors/](docs/executors/).

## MCP Integration

Agent Flows provides native support for Model Context Protocol (MCP) servers, enabling seamless integration with external tools and services.

### MCP Server Examples

```python
# Send email via Gmail MCP server
{
  "type": "mcpServerAction",
  "config": {
    "provider": "remote",
    "serverId": "GMAIL",
    "action": "GMAIL__SEND_EMAIL",
    "params": {
      "to": "recipient@example.com",
      "subject": "Hello from Agent Flows",
      "body": "This email was sent via MCP integration!"
    },
    "resultVariable": "email_result"
  }
}

# Upload file to Google Drive
{
  "type": "mcpServerAction",
  "config": {
    "provider": "remote",
    "serverId": "GOOGLE_DRIVE",
    "action": "DRIVE__UPLOAD_FILE",
    "params": {
      "fileName": "report.pdf",
      "fileContent": "${file_data}",
      "folderId": "${target_folder}"
    },
    "resultVariable": "upload_result"
  }
}
```

### Available MCP Servers

- **Gmail**: Email operations (send, read, manage)
- **Google Drive**: File operations (upload, download, organize)
- **Google Calendar**: Calendar management (create events, schedule meetings)
- **Slack**: Messaging and channel operations
- **Database**: Query execution and data management
- **File Manager**: Local file system operations

### MCP Configuration

Set up MCP integration using environment variables or configuration files:

```bash
# Environment variables
export MCP_ACI_API_KEY="your-aci-api-key"
export MCP_ACI_LINKED_ACCOUNT_OWNER_ID="your-linked-account-owner-id"
```

Or in your configuration:

```python
from agent_flows import AgentFlowsConfig
from agent_flows.models.config import MCPConfig

config = AgentFlowsConfig(
    mcp=MCPConfig(
        aci_api_key="your-aci-api-key",
        aci_linked_account_owner_id="your-linked-account-owner-id"
    )
)
```

## Architecture

The package follows a modular, extensible architecture:

```
agent_flows/
├── core/           # Core execution engine
├── executors/      # Block-specific executors
├── models/         # Pydantic data models
├── api/           # API client for flow fetching
├── cli/           # Command-line interface
└── utils/         # Utility functions
```

## API Reference

### FlowExecutor Methods

```python
# Constructor
FlowExecutor(
    config=None,           # AgentFlowsConfig: System configuration (uses env vars if None)
    flow_config=None,      # FlowConfig: Local flow configuration
    log_level="INFO",      # str: Logging level (e.g., "DEBUG", "INFO", "WARNING")
    log_json_format=False  # bool: Format logs as JSON
)

# Class methods
FlowExecutor.from_file(
    flow_file,            # str: Path to flow JSON file
    config=None,          # AgentFlowsConfig: System configuration (uses env vars if None)
)

FlowExecutor.from_dict(
    flow_dict,            # dict: Flow configuration dictionary
    config=None,          # AgentFlowsConfig: System configuration (uses env vars if None)
)

# Execution methods
await executor.execute_flow(
    flow_id=None,         # str: Flow UUID (optional if flow_config provided)
    variables=None,       # dict: Flow variables
    context=None          # dict: Additional execution context
)

executor.run(
    flow_id=None,         # str: Flow UUID (optional if flow_config provided)
    variables=None        # dict: Flow variables
)
```

### Configuration Types

**System Configuration** (`AgentFlowsConfig`): API credentials and LLM settings
**Flow Configuration** (`FlowConfig`): The actual flow definition with steps

## Demo

Try the comprehensive demo:

```bash
python demo_packaging.py
```

## Requirements

- Python 3.8+
- Dependencies: aiohttp, pydantic, click, litellm

## License

MIT License
