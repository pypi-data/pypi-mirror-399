# Web Scraping Executor

Scrape web pages through the `webScraping` step type and Crawl4AI-powered MCP service. This executor focuses on predictable, UI-friendly configuration while exposing Crawl4AI’s content scoping, filtering, and structured extraction features.

## Overview

- **Executor type**: `webScraping`
- **Engine**: `web-scraping-mcp-server` (Crawl4AI + managed browser)
- **Purpose**: download targeted page content, optionally clean/filter it, and return markdown, HTML, or structured payloads
- **Great for**: curated article capture, domain monitoring, compliance archiving, news or catalogue enrichment that feeds downstream LLMs or analytics

## Execution Flow

1. Step config is validated and flow variables are interpolated.
2. Crawl directives are translated into `CrawlerRunConfig` arguments plus LiteLLM environment hints.
3. The MCP client launches `web-scraping-mcp-server`, executes the crawl, and waits for the Crawl4AI response.
4. Scraped data (markdown/HTML/structured payload) is returned in `ExecutorResult.data`, optionally stored in `resultVariable`, or surfaced as `directOutput`.

## Configuration Schema

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `urls` | list\<string> | — | 1–100 unique HTTP(S) URLs to crawl. |
| `contentSelection` | object \| `null` | `null` | Optional scoping of page regions. |
| `contentFiltering` | object \| `null` | `null` | Optional filters for tags, links, media, iframes, overlays. |
| `outputFormat` | enum | `"markdown"` | `"markdown"`, `"html"`, or `"structured"`. |
| `outputOptions` | object \| `null` | `null` | Tunable options per output format. |
| `browser` | object \| `null` | `{headless: true, userAgentMode: "random", textMode: true}` | Browser session controls and proxy. |
| `page` | object \| `null` | `{timeoutMs: 60000, delayBeforeReturnHtml: 0.1}` | Page wait strategy, timeout, and HTML capture delay. |
| `retry` | object \| `null` | `{attempts: 2}` | MCP retry attempts (0–10). |
| `advanced` | object \| `null` | `null` | Optional Crawl4AI extras (tables, captures). |
| `resultVariable` | string \| `null` | `null` | Flow variable populated with `ExecutorResult.data`. |
| `directOutput` | boolean | `false` | If `true`, shortcut the flow result with executor data. |

### `contentSelection`

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `cssSelector` | string \| `null` | `null` | Single CSS selector to scope the crawl. Mutually exclusive with `targetElements`. |
| `targetElements` | list\<string> \| `null` | `null` | Multiple selectors for markdown focus while keeping wider context. |

### `contentFiltering`

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `excludedTags` | list\<string> | `[]` | Remove entire tags (e.g. `nav`, `footer`). |
| `wordCountThreshold` | integer | `0` | Minimum words per block before inclusion. |
| `links.excludeExternal` | boolean | `false` | Strip non-origin links. |
| `links.excludeSocialMedia` | boolean | `false` | Strip links that match the social list. |
| `links.excludeDomains` | list\<string> | `[]` | Custom domain blocklist. |
| `links.socialMediaDomains` | list\<string> \| `null` | `null` | Override/extend the default social domains. |
| `media.excludeExternalImages` | boolean | `false` | Ignore off-site images. |
| `processIframes` | boolean | `false` | Merge iframe content before filtering. |
| `removeOverlays` | boolean | `false` | Drop fixed overlays/popups where Crawl4AI supports it. |

### `outputOptions.markdown`

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `includeCitations` | boolean | `false` | Request markdown with inline citations. |
| `includeReferences` | boolean | `false` | Append reference section when citations are enabled. |
| `bodyWidth` | integer | `0` | Wrap markdown to the specified column width; `0` leaves formatting untouched. |

### `outputOptions.html`

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `variant` | enum | `"cleaned"` | `"raw"` (original HTML), `"cleaned"` (sanitised), `"fit"` (post-filtered). |

### `outputOptions.structured`

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `method` | enum | — | `"css"` or `"llm"` (required). |
| `css.baseSelector` | string | — | Root selector for repeated blocks. |
| `css.fields[]` | object | — | Field schema (name, selector, type, optional attribute/nested fields). |
| `llm.provider` | string \| `null` | `null` | LiteLLM provider name (e.g. `"openai"`, `"realtimexai"`). |
| `llm.model` | string \| `null` | `null` | Provider-specific model identifier. |
| `llm.instruction` | string | — | Prompt sent to the extraction strategy. |
| `llm.temperature` | float | `0.0` | Temperature forwarded to the LLM. |
| `llm.extractionType` | enum | — | `"schema"` (structured JSON) or `"block"` (aggregated text/fragments). |
| `llm.schema` | object \| `null` | `null` | Required when `extractionType="schema"`; JSON Schema describing the desired payload. Must be omitted for `"block"`. |

### `browser`

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `headless` | boolean | `true` | Disable browser UI for faster crawls. |
| `userAgentMode` | enum | `"random"` | `"random"` or `"default"`. |
| `userAgent` | string \| `null` | `null` | Required when `userAgentMode="default"`. |
| `textMode` | boolean | `true` | Disable images for speed; set `false` when screenshots or rich media matter. |
| `proxy.server` | string | — | Proxy URL (`http`, `https`, `socks4`, `socks5`). |
| `proxy.username` / `proxy.password` | string \| `null` | `null` | Optional basic-auth credentials. |

### `page`, `retry`, and `advanced`

| Section | Field | Type | Default | Notes |
|---------|-------|------|---------|-------|
| `page` | `waitFor` | string \| `null` | `null` | `css:` or `js:` prefixed condition evaluated before extraction. |
|  | `timeoutMs` | integer | `60000` | Page load timeout in milliseconds. |
|  | `delayBeforeReturnHtml` | float | `0.1` | Pause (seconds) before final HTML is captured. |
| `retry` | `attempts` | integer | `2` | Retry count for MCP invocation. |
| `advanced` | `tableScoreThreshold` | integer \| `null` | `null` | Minimum table score before inclusion. |
|  | `captureScreenshot` / `capturePdf` / `captureMhtml` | boolean | `false` | Request additional artefacts when the MCP server enables them. |

## Usage

### Minimal Markdown Crawl
```json
{
  "type": "webScraping",
  "config": {
    "urls": ["https://example.com/article"],
    "outputFormat": "markdown"
  }
}
```

### Targeted Article Markdown with Filtering
```json
{
  "type": "webScraping",
  "config": {
    "urls": ["https://example.com/news"],
    "contentSelection": {"targetElements": ["article.main-content"]},
    "contentFiltering": {
      "excludedTags": ["nav", "footer", "aside"],
      "wordCountThreshold": 20,
      "links": {"excludeSocialMedia": true}
    },
    "outputFormat": "markdown",
    "outputOptions": {
      "markdown": {"includeCitations": true, "includeReferences": true}
    },
    "resultVariable": "article_markdown"
  }
}
```

### Structured CSS Extraction
```json
{
  "type": "webScraping",
  "config": {
    "urls": ["https://news.ycombinator.com"],
    "outputFormat": "structured",
    "outputOptions": {
      "structured": {
        "method": "css",
        "css": {
          "baseSelector": ".athing",
          "fields": [
            {"name": "title", "selector": ".titleline a", "type": "text"},
            {"name": "link", "selector": ".titleline a", "type": "attribute", "attribute": "href"}
          ]
        }
      }
    },
    "resultVariable": "stories"
  }
}
```

### LLM Block Extraction
```json
{
  "type": "webScraping",
  "config": {
    "urls": ["https://example.com/analysis"],
    "outputFormat": "structured",
    "outputOptions": {
      "structured": {
        "method": "llm",
        "llm": {
          "provider": "openai",
          "model": "gpt-4o-mini",
          "instruction": "Summarise the three most important insights in bullet form.",
          "extractionType": "block"
        }
      }
    },
    "directOutput": true
  }
}
```

## Operational Notes

- The executor streams status via the shared `StreamingHandler`; long crawls surface progress updates when URLs are queued.
- All Crawl4AI errors (timeouts, navigation failures, extraction issues) are wrapped in `ExecutorError` with context-rich messaging.
- LLM extractions rely on LiteLLM credentials provided in the global configuration or resolved through the credential manager; ensure providers are preconfigured.

## Future Enhancements

Planned improvements that surfaced during design and review:

- **Configurable entrypoint** – richer control over how multi-step scrape → transform flows are invoked (e.g., named operations exposed by the MCP server).
- **Structured output mapping** – allow multi-channel responses (markdown + structured JSON) without extra flow glue.
- **Environment injection** – declaratively pass secrets or static headers into the MCP process for cases that need authenticated crawls.

These are not implemented yet but inform the longer-term roadmap for the executor and MCP server.
