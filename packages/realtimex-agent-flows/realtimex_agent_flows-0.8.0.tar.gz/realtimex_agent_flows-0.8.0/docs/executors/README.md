# Agent Flows Executors Documentation

This directory contains comprehensive documentation for all Agent Flows executors, including implementation guides, configuration references, and usage examples.

## Available Executors

Agent Flows currently supports **8 built-in executors**:

| Executor | Type | Purpose | Documentation |
|----------|------|---------|---------------|
| **Flow Variables** | `flow_variables` (alias: `start`) | Initialize flow variables and context | [start/](./start/) |
| **API Call** | `apiCall` | Make HTTP requests to external APIs | [api_call/](./api_call/) |
| **LLM Instruction** | `llmInstruction` | Execute LLM-powered text processing | [llm_instruction/](./llm_instruction/) |
| **Web Scraping** | `webScraping` | Extract content from web pages | [web_scraping/](./web_scraping/) |
| **Conditional** | `conditional` | Execute blocks based on conditions | [conditional/](./conditional/) |
| **Switch** | `switch` | Route execution based on variable values | [switch/](./switch/) |
| **Loop** | `loop` | Iterate execution with for/while/forEach | [loop/](./loop/) |
| **MCP Server Action** | `mcpServerAction` | Execute actions on MCP servers | [mcp_server_action/](./mcp_server_action/) |

> `start` remains a deprecated alias for `flow_variables` so existing flows keep
> running. Use the canonical name when defining new steps.

## Documentation Structure

### Executor-Specific Documentation
Each executor has dedicated documentation covering:
- **Configuration Schema**: Required and optional fields
- **Usage Examples**: Real-world configuration examples
- **Variable Interpolation**: How to use `{{ $variable }}` syntax
- **Error Handling**: Common errors and troubleshooting
- **Integration Patterns**: How to combine with other executors
- **Performance Considerations**: Best practices and limitations

### Development Documentation
- **[Executor Development Guide](./executor-development.md)**: Guidelines for creating new executors
- **[Adding New Executors](./adding-new-executors.md)**: Step-by-step checklist for implementation

## Quick Reference

### Basic Executor Structure
```json
{
  "type": "executorType",
  "config": {
    "requiredField": "value",
    "optionalField": "value",
    "resultVariable": "variable_name"
  }
}
```

### Variable Interpolation
All executors support variable interpolation using `{{ $variable }}` syntax:
```json
{
  "type": "apiCall",
  "config": {
    "url": "https://api.example.com/users/{{ $user_id }}",
    "method": "GET",
    "responseVariable": "user_data"
  }
}
```

### Common Configuration Fields
Most executors support these optional fields:
- `resultVariable`: Variable name to store execution results
- `directOutput`: Return results directly without storing
- `timeout`: Execution timeout in seconds

## Testing Executors

### Individual Executor Testing
```bash
# Test a specific executor
python scripts/test_cli.py executor <executor_type>

# Examples
python scripts/test_cli.py executor loop
python scripts/test_cli.py executor apiCall
python scripts/test_cli.py executor conditional
```

### Workflow Testing
```bash
# Test executors in workflows
python scripts/test_cli.py workflow simple_api_call
python scripts/test_cli.py workflow complex_multi_step
```

### Test Suites
```bash
# Run all executor tests
python scripts/test_cli.py suite basic_executors

# List available tests
python scripts/test_cli.py list
```

## Integration Examples

### Sequential Execution
```json
{
  "steps": [
    {
      "type": "start",
      "config": {
        "variables": [{"name": "user_id", "value": "123"}]
      }
    },
    {
      "type": "apiCall",
      "config": {
        "url": "https://api.example.com/users/{{ $user_id }}",
        "method": "GET",
        "responseVariable": "user_data"
      }
    },
    {
      "type": "llmInstruction",
      "config": {
        "instruction": "Analyze this user data: {{ $user_data }}",
        "resultVariable": "analysis"
      }
    }
  ]
}
```

### Conditional Logic
```json
{
  "type": "conditional",
  "config": {
    "condition": {
      "variable": "user_data.status",
      "operator": "equals",
      "value": "active"
    },
    "truePath": [
      {
        "type": "apiCall",
        "config": {
          "url": "https://api.example.com/activate/{{ $user_id }}",
          "method": "POST"
        }
      }
    ],
    "falsePath": [
      {
        "type": "llmInstruction",
        "config": {
          "instruction": "Generate inactive user message",
          "resultVariable": "message"
        }
      }
    ]
  }
}
```

### Iterative Processing
```json
{
  "type": "loop",
  "config": {
    "loopType": "forEach",
    "iterableVariable": "user_list",
    "itemVariable": "user",
    "loopBlocks": [
      {
        "type": "apiCall",
        "config": {
          "url": "https://api.example.com/process/{{ $user.id }}",
          "method": "POST",
          "responseVariable": "result"
        }
      }
    ]
  }
}
```

## Error Handling

### Common Error Types
- **Configuration Errors**: Invalid or missing required fields
- **Runtime Errors**: Network failures, API errors, processing failures
- **Variable Errors**: Missing variables, interpolation failures
- **Timeout Errors**: Execution exceeding time limits

### Error Response Structure
```json
{
  "success": false,
  "error": "Error description",
  "error_type": "ConfigurationError",
  "flow_id": "flow-uuid",
  "step_index": 2,
  "step_type": "apiCall"
}
```

## Best Practices

### Configuration
- Use descriptive variable names
- Set appropriate timeouts for external calls
- Validate required fields before deployment
- Use variable interpolation for dynamic values

### Performance
- Minimize API calls in loops
- Use appropriate batch sizes for data processing
- Set reasonable iteration limits
- Monitor execution times and resource usage

### Security
- Avoid exposing sensitive data in logs
- Use secure API endpoints (HTTPS)
- Validate input data before processing
- Implement proper error handling

## Contributing

When adding new executors or updating documentation:

1. Follow the [Adding New Executors](./adding-new-executors.md) checklist
2. Create comprehensive documentation following the Loop Executor example
3. Include configuration examples and use cases
4. Add unit tests with >90% coverage
5. Update this README with the new executor information

## Support

For questions, issues, or contributions:
- Review the executor-specific documentation
- Check the development guides
- Run the test suite to verify functionality
- Follow the established patterns and conventions