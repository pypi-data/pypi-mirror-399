# News Analyst Flow - Production Ready

A comprehensive, production-ready workflow for analyzing breaking news headlines and producing detailed macroeconomic reports for trading decisions.

## Overview

This flow is part of a Financial Analysis system alongside Fundamental Analyst, Market Analyst, and Social Analyst flows. It transforms breaking news headlines into comprehensive, actionable intelligence through systematic discovery, analysis, and reporting.

## Current Implementation Status

**Phase 1: Complete** - Discovery and URL Selection
- ✅ Query generation (simple/enhanced/auto modes)
- ✅ Web search discovery with 7-day recency filter
- ✅ Intelligent URL ranking and selection
- ✅ Candidate URL validation and quality assessment

**Phase 2: Planned** - Content Analysis and Reporting
- 🔄 URL scraping and content extraction
- 🔄 Per-URL analysis and fact extraction
- 🔄 Cross-source consolidation and validation
- 🔄 Comprehensive report generation
- 🔄 Multi-channel delivery (email/slack/markdown/linkedin)

## Features

### Query Generation Modes
- **Simple**: Uses headline as-is for search
- **Enhanced**: LLM-generated 2-4 optimized queries
- **Auto**: Starts simple, enhances if results are insufficient

### Intelligent Discovery
- Recent news focus (7-day window)
- Multiple search queries for comprehensive coverage
- Deduplication and result consolidation
- Credible source prioritization

### URL Selection Criteria
- Credible sources (major news outlets, financial publications)
- Recent articles (prefer 48h, max 7 days)
- Relevance to headline and topic
- Diversity across sources
- Integration of primary URL when valid
- Bias toward interested tickers/industries

## Input Parameters

### Required
- `breaking_news_headline`: The news headline to analyze
- `breaking_news_primary_url`: Primary URL associated with the news
- `received_at`: ISO 8601 timestamp of alert receipt
- `publisher`: Source of the alert (e.g., "CNBC", "Reuters")
- `topic_hint`: Topic category ("earnings", "macro", "M&A", "regulatory", "")
- `output_channel`: Delivery method ("email", "markdown", "slack", "linkedin")
- `recipient`: Target for delivery (email address, channel, etc.)

### Optional
- `interested_tickers`: Array of ticker symbols for focused analysis
- `interested_industries`: Array of industry names for sector focus
- `max_urls`: Maximum URLs to analyze (default: 5)
- `query_mode`: Query generation approach ("auto", "simple", "enhanced")

## Usage

### CLI Execution
```bash
# Run with default variables
agent-flows run examples/3_workflows/5_news-analyst/flow.json

# Run with custom variables
agent-flows run examples/3_workflows/5_news-analyst/flow.json \
  --variables-file examples/3_workflows/5_news-analyst/variables.json

# Run with inline variables
agent-flows run examples/3_workflows/5_news-analyst/flow.json \
  --variables '{"breaking_news_headline":"Tesla Announces New Gigafactory","breaking_news_primary_url":"https://tesla.com/news","received_at":"2025-01-15T10:00:00Z","publisher":"Tesla","topic_hint":"expansion","output_channel":"email","recipient":"analyst@example.com"}'
```

### Python Integration
```python
from agent_flows import FlowExecutor

# Load flow
executor = FlowExecutor.from_file(
    flow_file="examples/3_workflows/5_news-analyst/flow.json"
)

# Execute with variables
result = await executor.execute_flow(
    variables={
        "breaking_news_headline": "Fed Announces Emergency Rate Cut",
        "breaking_news_primary_url": "https://federalreserve.gov/newsevents/",
        "received_at": "2025-01-15T15:30:00Z",
        "publisher": "Federal Reserve",
        "topic_hint": "macro",
        "output_channel": "email",
        "recipient": "trader@firm.com",
        "interested_tickers": ["SPY", "QQQ", "TLT"],
        "interested_industries": ["banking", "technology"]
    }
)
```

## Output (Phase 1)

The current implementation returns:
- **Query Generation Results**: Generated search queries and approach used
- **Search Discovery**: Number of results found and source diversity
- **Candidate URLs**: Selected URLs with quality assessment
- **Phase 1 Summary**: Comprehensive execution status and readiness for Phase 2

Example output structure:
```json
{
  "success": true,
  "candidate_urls_final": {
    "candidate_urls": [
      "https://www.apple.com/newsroom/...",
      "https://www.cnbc.com/...",
      "https://www.reuters.com/..."
    ],
    "url_count": 3,
    "quality_assessment": "High-quality mix of official and financial news sources",
    "validation_status": "passed"
  },
  "phase1_summary": "Detailed execution summary..."
}
```

## Configuration

### Search Provider
Currently configured for Google Custom Search. Update the `webSearch` executor configuration:
```json
{
  "provider": {
    "name": "google",
    "config": {
      "apiKey": "your-google-api-key",
      "searchEngineId": "your-search-engine-id"
    }
  }
}
```

### LLM Settings
Uses `gpt-4o-mini` for cost-effective analysis. Adjust model and parameters as needed:
```json
{
  "model": "gpt-4o-mini",
  "temperature": 0.2,
  "maxTokens": 1000
}
```

## Error Handling

- **No Search Results**: Falls back to primary URL only
- **Invalid URLs**: Validates and filters candidate URLs
- **Query Generation Failure**: Retries with exponential backoff
- **Search API Limits**: Implements retry logic with rate limiting

## Testing

Test the Phase 1 implementation:
```bash
# Test with sample variables
python scripts/test_cli.py workflow examples/3_workflows/5_news-analyst/flow.json

# Test specific scenarios
agent-flows run examples/3_workflows/5_news-analyst/flow.json \
  --variables '{"breaking_news_headline":"Market Volatility Increases","query_mode":"enhanced",...}'
```

## Next Steps (Phase 2)

1. **Content Scraping**: Implement robust web scraping for selected URLs
2. **Per-URL Analysis**: Extract facts, numbers, entities, and quotes
3. **Cross-Source Validation**: Consolidate and validate information across sources
4. **Report Generation**: Create comprehensive macroeconomic reports
5. **Multi-Channel Delivery**: Implement email, Slack, and other delivery methods
6. **Interest Tailoring**: Apply ticker/industry focus to final reports

## Production Considerations

- **Rate Limiting**: Implement appropriate delays for search APIs
- **Caching**: Cache search results to avoid redundant API calls
- **Monitoring**: Add telemetry for execution tracking and performance
- **Scaling**: Consider parallel processing for multiple headlines
- **Security**: Secure API keys and sensitive configuration data

## Dependencies

- Google Custom Search API (for web search)
- OpenAI API (for LLM processing)
- Agent Flows runtime environment

## Version History

- **v1.0.0**: Phase 1 implementation - Discovery and URL selection
- **v2.0.0**: Planned - Full analysis and reporting pipeline