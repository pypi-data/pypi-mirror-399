# Agent Flow Executors Test Framework

A comprehensive, modular test framework for Agent Flow executors that provides consistent testing across CLI and API interfaces.

## Quick Start

### 1. Setup Test Environment

```bash
# Setup test environment with sample configurations
python scripts/test_cli.py setup
```

This creates:
- `.env` file from `.env.example` (if not exists)
- Sample flow configurations in `examples/`
- Test suites in `tests/fixtures/suites/`

### 2. Run Individual Tests

```bash
# Test individual executors
python scripts/test_cli.py executor start
python scripts/test_cli.py executor apiCall
python scripts/test_cli.py executor llmInstruction
python scripts/test_cli.py executor webScraping

# Test workflows
python scripts/test_cli.py workflow simple_start
python scripts/test_cli.py workflow api_to_llm
python scripts/test_cli.py workflow complex_multi_step

# Test from flow files
python scripts/test_cli.py flow examples/start_executor_test.json
python scripts/test_cli.py flow examples/complex_multi_step.json --variables '{"user_id": "123"}'
```

### 3. Run Test Suites

```bash
# Run predefined test suites
python scripts/test_cli.py suite basic_executors
python scripts/test_cli.py suite workflow_tests
python scripts/test_cli.py suite integration_tests
```

### 4. List Available Tests

```bash
python scripts/test_cli.py list
```

### 5. Validate Environment

```bash
python scripts/test_cli.py validate
```

## API Usage

You can also use the test framework programmatically:

```python
import asyncio
from tests.api import AgentFlowTestAPI

async def main():
    api = AgentFlowTestAPI()
    
    # Setup environment
    await api.setup_environment()
    
    # Run individual tests
    result = await api.run_executor_test("start")
    print(result)
    
    # Run workflow test
    result = await api.run_workflow_test("simple_start")
    print(result)
    
    # Run all tests
    result = await api.run_all_tests()
    print(result)

asyncio.run(main())
```

Or use the convenience functions:

```python
from tests.api import run_executor_test_sync, run_all_tests_sync

# Synchronous usage
result = run_executor_test_sync("start")
all_results = run_all_tests_sync()
```

## Framework Structure

```
tests/
├── README.md                 # This file
├── test_runner.py            # Main test runner
├── api.py                    # API interface
├── conftest.py              # Pytest configuration
├── fixtures/                # Test fixtures and data
│   ├── flows/
│   │   ├── executors/       # JSON fixtures for executor tests
│   │   └── workflows/       # JSON fixtures for workflow tests
│   ├── suites/              # JSON fixtures for test suites
│   └── flow_fixtures.py     # Fixture loading logic
├── runners/                 # Test execution engines
│   ├── executor_runner.py   # Individual executor tests
│   └── workflow_runner.py   # Workflow tests
├── utils/                   # Utilities
│   ├── test_logger.py       # Enhanced logging
│   ├── test_validator.py    # Configuration validation
│   └── mock_responses.py    # Mock data for testing
├── unit/                    # Unit tests
└── integration/             # Integration tests
```

## Test Types

### Executor Tests
Test individual executors in isolation:
- **start**: Variable initialization
- **apiCall**: HTTP API calls
- **llmInstruction**: LLM interactions
- **webScraping**: Web content extraction

### Workflow Tests
Test complete multi-step workflows:
- **simple_start**: Basic variable initialization (start executor only)
- **simple_api_call**: API call test (start + API call executors)
- **simple_llm_instruction**: LLM instruction test (start + LLM executors)
- **simple_web_scraping**: Web scraping test (start + web scraping executors)
- **api_to_llm**: API call followed by LLM processing (multi-step)
- **web_scrape_analyze**: Web scraping with LLM analysis (multi-step)
- **complex_multi_step**: Full workflow with all executor types

### Test Suites
Predefined collections of tests:
- **basic_executors**: All individual executor tests
- **workflow_tests**: All workflow tests
- **integration_tests**: End-to-end integration tests

## Configuration

### Environment Variables

The framework uses these environment variables (set in `.env`):

```bash
# Core configuration
AGENT_FLOWS_API_KEY=your-api-key
AGENT_FLOWS_BASE_URL=https://your-instance.com
AGENT_FLOWS_TIMEOUT=30
AGENT_FLOWS_MAX_RETRIES=3

# LLM configuration
LITELLM_API_KEY=your-openai-key
LITELLM_API_BASE=https://api.openai.com/v1

# Test-specific configuration
TEST_MODE=true                    # Enable test mode
TEST_MOCK_API_CALLS=true         # Mock API calls
TEST_MOCK_LLM_CALLS=true         # Mock LLM calls
TEST_MOCK_WEB_SCRAPING=true      # Mock web scraping
```

### Mock Responses

In test mode, the framework uses mock responses instead of real API calls:
- API calls return predefined JSON responses
- LLM calls return contextual mock text
- Web scraping returns sample HTML content

This ensures tests are fast, reliable, and don't require external services.

## Performance Testing

Run performance tests to measure execution times:

```bash
# Test executor performance
python scripts/test_cli.py performance executor start --iterations 20

# Test workflow performance
python scripts/test_cli.py performance workflow simple_start --iterations 10
```

## Integration with uvx

The framework works seamlessly with uvx for package execution:

```bash
# Install and run via uvx
uvx agent-flows test executor start
uvx agent-flows test workflow simple_start
uvx agent-flows test suite basic_executors
```

## Extending the Framework

Adding new tests is designed to be simple and requires no code changes for test discovery.

### Adding New Executor Tests

1.  **Create a JSON file** in `tests/fixtures/flows/executors/`.
    *   The filename (e.g., `myNewExecutor.json`) determines the test name.
    *   The CLI will automatically discover this new test.

2.  **Define the test configuration** in the JSON file:

    ```json
    {
      "name": "My New Executor Test",
      "description": "Test my new executor",
      "config": {
        "param1": "value1",
        "param2": "value2"
      },
      "variables": {
        "initial_variable": "some_value"
      }
    }
    ```

3.  **Run the test** using the filename as the executor type:
    ```bash
    python scripts/test_cli.py executor myNewExecutor
    ```

### Adding New Workflows

1.  **Create a JSON file** in `tests/fixtures/flows/workflows/`.
    *   The filename (e.g., `my_new_workflow.json`) determines the test name.

2.  **Define the workflow** in the JSON file. This is a standard Agent Flow file:

    ```json
    {
      "name": "My New Workflow",
      "description": "A new test workflow",
      "uuid": "00000000-0000-0000-0000-000000000000",
      "active": true,
      "steps": [
        {
          "type": "start",
          "config": { ... }
        },
        {
          "type": "myNewExecutor",
          "config": { ... }
        }
      ]
    }
    ```

3.  **Run the workflow** using its name:
    ```bash
    python scripts/test_cli.py workflow my_new_workflow
    ```

### Adding New Test Suites

Create a new JSON file in `tests/fixtures/suites/`. The structure remains the same, referencing the executor or workflow tests by their name (which is their filename without the `.json` extension).

## Best Practices

1. **Always run setup first**: `python scripts/test_cli.py setup`
2. **Use test mode**: Keep `TEST_MODE=true` for reliable testing
3. **Validate environment**: Run `validate` command before important tests
4. **Use appropriate test types**: Unit tests for individual components, integration tests for workflows
5. **Check logs**: Use `--log-level DEBUG` for detailed information
6. **Performance testing**: Use performance tests to catch regressions

## Troubleshooting

### Common Issues

1. **"No test configuration found"**: Run setup command first
2. **"Environment validation failed"**: Check `.env` file configuration
3. **"Import errors"**: Ensure you're running from the project root
4. **"API key errors"**: Set proper API keys in `.env` or enable test mode

### Debug Mode

Enable debug logging for detailed information:

```bash
python scripts/test_cli.py --log-level DEBUG executor start
```

This provides detailed execution logs, mock response information, and validation details.