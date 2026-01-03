"""WebScrapingExecutor for web content extraction using Crawl4AI."""

import json
import time
from typing import Any

from pydantic import ValidationError

from agent_flows.core.resources.interpolation import VariableInterpolator
from agent_flows.exceptions import (
    ConfigurationError,
    ExecutorError,
    MCPConnectionError,
    MCPError,
    MCPTimeoutError,
    MCPToolError,
)
from agent_flows.executors.base import BaseExecutor
from agent_flows.integrations import LLMProviderManager, MCPClient
from agent_flows.models.execution import ExecutionContext, ExecutorResult
from agent_flows.models.executors import WebScrapingExecutorConfig
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class WebScrapingExecutor(BaseExecutor):
    """Executor for web scraping using Crawl4AI."""

    def __init__(self) -> None:
        """Initialize the web scraping executor."""
        self.interpolator = VariableInterpolator()

    def get_required_fields(self) -> list[str]:
        """Get list of required configuration fields."""
        return ["urls", "outputFormat"]

    def get_optional_fields(self) -> list[str]:
        """Get list of optional configuration fields."""
        return [
            "contentSelection",
            "contentFiltering",
            "outputOptions",
            "browser",
            "page",
            "retry",
            "advanced",
            "resultVariable",
            "directOutput",
        ]

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate web scraping configuration."""
        try:
            WebScrapingExecutorConfig(**config)
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Web scraping executor configuration validation failed: {str(e)}"
            ) from e

    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Execute web scraping using Crawl4AI."""
        start_time = time.time()

        try:
            interpolated_config = self.interpolator.interpolate_object(config, context.variables)
            validated_config = WebScrapingExecutorConfig(**interpolated_config)

            log.info(
                "Starting web scraping execution",
                urls=validated_config.urls,
                output_format=validated_config.outputFormat,
                url_count=len(validated_config.urls),
            )

            if context.step_execution_service and context.step_execution_service.streaming_handler:
                urls = validated_config.urls
                if urls:
                    first_url = urls[0]
                    if len(urls) > 1:
                        content = f"Scraping {len(urls)} URLs starting with {first_url}"
                    else:
                        content = f"Scraping {first_url}"
                else:
                    content = "Scraping with no URLs provided"
                context.step_execution_service.streaming_handler.stream_step(
                    "Web Scraping", "Download", content, content
                )

            scraping_results = await self._execute_with_retries(validated_config, context)

            variables_updated: dict[str, Any] = {}
            if validated_config.resultVariable:
                variables_updated[validated_config.resultVariable] = scraping_results

            execution_time = time.time() - start_time

            log.info(
                "Web scraping completed",
                execution_time=round(execution_time, 2),
                urls_processed=len(scraping_results.get("results", [])),
                successful_urls=scraping_results.get("summary", {}).get("successful", 0),
            )

            return ExecutorResult(
                success=True,
                data=scraping_results,
                variables_updated=variables_updated,
                direct_output=validated_config.directOutput,
                execution_time=execution_time,
                metadata={
                    "urls": validated_config.urls,
                    "output_format": validated_config.outputFormat,
                    "urls_processed": len(scraping_results.get("results", [])),
                    "step_type": "webScraping",
                },
            )

        except ConfigurationError:
            raise
        except Exception as e:
            raise ExecutorError(f"Web scraping execution failed: {str(e)}") from e

    async def _execute_with_retries(
        self,
        config: WebScrapingExecutorConfig,
        context: ExecutionContext,
    ) -> dict[str, Any]:
        """Execute web scraping with retry support."""
        try:
            return await self._execute_mcp_scraping(config, context)
        except Exception as e:
            raise ExecutorError(f"Web scraping failed: {str(e)}") from e

    async def _execute_mcp_scraping(
        self,
        config: WebScrapingExecutorConfig,
        context: ExecutionContext,
    ) -> dict[str, Any]:
        """Execute web scraping using the MCP server."""
        mcp_client = None
        try:
            mcp_client = MCPClient()

            mcp_env = self._build_mcp_environment(config, context)

            await mcp_client.connect_to_server(
                command="web-scraping-mcp-server",
                args=[],
                env=mcp_env,
            )

            arguments = self._build_scraping_arguments(config)

            log.debug(
                "Calling MCP web_scrape tool",
                tool_name="web_scrape",
                urls=config.urls,
                output_format=config.outputFormat,
            )

            result = await mcp_client.call_tool(
                tool_name="web_scrape",
                arguments=arguments,
                timeout=config.get_page_config().timeoutMs // 1000,
            )

            return self._process_mcp_response(result)

        except (MCPConnectionError, MCPTimeoutError, MCPToolError, MCPError) as e:
            raise ExecutorError(f"MCP web scraping failed: {str(e)}") from e
        except Exception as e:
            raise ExecutorError(f"Unexpected error during MCP web scraping: {str(e)}") from e
        finally:
            if mcp_client:
                await mcp_client.disconnect()

    def _build_mcp_environment(
        self, config: WebScrapingExecutorConfig, context: ExecutionContext
    ) -> dict[str, str]:
        """Build environment variables for the MCP server."""
        env_vars: dict[str, str] = {}

        litellm_config = context.config.litellm
        if litellm_config.api_base:
            env_vars["LITELLM_API_BASE"] = litellm_config.api_base
        if litellm_config.api_key:
            env_vars["LITELLM_API_KEY"] = litellm_config.api_key

        # Add LLM provider credentials for structured extraction
        if (
            config.outputFormat == "structured"
            and config.outputOptions
            and config.outputOptions.structured
            and config.outputOptions.structured.method == "llm"
            and config.outputOptions.structured.llm
        ):
            llm_config = config.outputOptions.structured.llm
            if llm_config.provider:
                try:
                    providers_config = {
                        name: provider_config.credentials
                        for name, provider_config in context.config.llm_providers.providers.items()
                    }
                    manager = LLMProviderManager(providers=providers_config)
                    provider_env_vars = manager.get_provider_env_vars(llm_config.provider)
                    env_vars.update(provider_env_vars)
                    log.debug(
                        "Added LLM provider environment for MCP server",
                        provider=llm_config.provider,
                    )
                except ExecutorError as e:
                    raise ExecutorError(
                        f"Failed to configure LLM provider for web scraping: {e}"
                    ) from e

        return env_vars

    def _build_scraping_arguments(self, config: WebScrapingExecutorConfig) -> dict[str, Any]:
        """Build arguments for the web_scrape MCP tool."""
        arguments: dict[str, Any] = {
            "urls": config.urls,
            "outputFormat": config.outputFormat,
        }

        # Content selection
        if config.contentSelection:
            content_selection = {}
            if config.contentSelection.cssSelector:
                content_selection["cssSelector"] = config.contentSelection.cssSelector
            if config.contentSelection.targetElements:
                content_selection["targetElements"] = config.contentSelection.targetElements
            # Only add if we have actual content
            if content_selection:
                arguments["contentSelection"] = content_selection

        # Content filtering
        if config.contentFiltering:
            filtering = {}
            if config.contentFiltering.excludedTags:
                filtering["excludedTags"] = config.contentFiltering.excludedTags
            if config.contentFiltering.wordCountThreshold is not None:
                filtering["wordCountThreshold"] = config.contentFiltering.wordCountThreshold
            if config.contentFiltering.links:
                filtering["links"] = {
                    "excludeExternal": config.contentFiltering.links.excludeExternal,
                    "excludeSocialMedia": config.contentFiltering.links.excludeSocialMedia,
                    **(
                        {"excludeDomains": config.contentFiltering.links.excludeDomains}
                        if config.contentFiltering.links.excludeDomains
                        else {}
                    ),
                }
            if config.contentFiltering.media:
                filtering["media"] = {
                    "excludeExternalImages": config.contentFiltering.media.excludeExternalImages
                }
            if config.contentFiltering.processIframes:
                filtering["processIframes"] = True
            if config.contentFiltering.removeOverlays:
                filtering["removeOverlays"] = True
            # Only add if we have actual content
            if filtering:
                arguments["contentFiltering"] = filtering

        # Output options
        if config.outputOptions:
            output_options = {}

            if config.outputOptions.markdown:
                output_options["markdown"] = {
                    "includeCitations": config.outputOptions.markdown.includeCitations,
                    "includeReferences": config.outputOptions.markdown.includeReferences,
                    "bodyWidth": config.outputOptions.markdown.bodyWidth,
                }

            if config.outputOptions.html:
                output_options["html"] = {"variant": config.outputOptions.html.variant}

            if config.outputOptions.structured:
                structured_config = config.outputOptions.structured
                structured_options = {"method": structured_config.method}

                if structured_config.method == "css" and structured_config.css:
                    structured_options["css"] = {
                        "baseSelector": structured_config.css.baseSelector,
                        "fields": self._serialize_css_fields(structured_config.css.fields),
                    }

                if structured_config.method == "llm" and structured_config.llm:
                    llm_config = structured_config.llm
                    llm_options = {
                        "instruction": llm_config.instruction,
                        "temperature": llm_config.temperature,
                        "extractionType": llm_config.extractionType,
                    }

                    if llm_config.provider:
                        model_string = self._build_crawl4ai_model_string(
                            llm_config.provider, llm_config.model
                        )
                        llm_options["provider"] = llm_config.provider
                        llm_options["model"] = model_string
                    elif llm_config.model != "auto":
                        llm_options["model"] = llm_config.model

                    if llm_config.schema_config:
                        llm_options["schema"] = {
                            "type": llm_config.schema_config.type,
                            "properties": llm_config.schema_config.properties,
                            **(
                                {"required": llm_config.schema_config.required}
                                if llm_config.schema_config.required
                                else {}
                            ),
                        }

                    structured_options["llm"] = llm_options

                output_options["structured"] = structured_options

            # Only add if we have actual content
            if output_options:
                arguments["outputOptions"] = output_options

        # Browser configuration
        if config.browser:
            browser_config = {
                "headless": config.browser.headless,
                "userAgentMode": config.browser.userAgentMode.value,
                "textMode": config.browser.textMode,
            }
            if config.browser.userAgent:
                browser_config["userAgent"] = config.browser.userAgent
            if config.browser.proxy:
                browser_config["proxy"] = {
                    "server": config.browser.proxy.server,
                    **(
                        {"username": config.browser.proxy.username}
                        if config.browser.proxy.username
                        else {}
                    ),
                    **(
                        {"password": config.browser.proxy.password}
                        if config.browser.proxy.password
                        else {}
                    ),
                }
            arguments["browser"] = browser_config

        # Page configuration
        if config.page:
            page_config = {
                "timeoutMs": config.page.timeoutMs,
                "delayBeforeReturnHtml": config.page.delayBeforeReturnHtml,
            }
            if config.page.waitFor:
                page_config["waitFor"] = config.page.waitFor
            arguments["page"] = page_config

        # Retry configuration
        if config.retry:
            arguments["retry"] = {"attempts": config.retry.attempts}

        # Advanced configuration
        if config.advanced:
            arguments["advanced"] = {
                "tableScoreThreshold": config.advanced.tableScoreThreshold,
                "captureScreenshot": config.advanced.captureScreenshot,
                "capturePdf": config.advanced.capturePdf,
                "captureMhtml": config.advanced.captureMhtml,
            }

        return arguments

    def _serialize_css_fields(self, fields: list) -> list[dict[str, Any]]:
        """Serialize CSS field configurations for MCP."""
        result = []
        for field in fields:
            field_dict = {
                "name": field.name,
                "selector": field.selector,
                "type": field.type,
            }
            if field.attribute:
                field_dict["attribute"] = field.attribute
            if field.fields:
                field_dict["fields"] = self._serialize_css_fields(field.fields)
            result.append(field_dict)
        return result

    def _build_crawl4ai_model_string(self, provider: str, model: str) -> str:
        """Build Crawl4AI model string in provider/model format."""
        if provider == "realtimexai":
            return model

        if "/" in model:
            return model
        else:
            return f"{provider}/{model}"

    def _process_mcp_response(self, mcp_result: dict[str, Any]) -> dict[str, Any]:
        """Process the MCP tool response."""
        content = mcp_result.get("content", mcp_result)

        if isinstance(content, str):
            try:
                content = json.loads(content)
            except (json.JSONDecodeError, TypeError) as e:
                raise ExecutorError(f"MCP server returned error: {content}") from e

        if not isinstance(content, dict):
            raise ExecutorError(f"Unexpected MCP response format: {type(content)}")

        if "success" not in content or "results" not in content or "summary" not in content:
            raise ExecutorError("MCP response missing required fields (success, results, summary)")

        # Clean up metadata from results
        if "results" in content and isinstance(content["results"], list):
            for result_item in content["results"]:
                if isinstance(result_item, dict):
                    result_item.pop("metadata", None)

        return content

    def get_step_type(self) -> str:
        """Return the step type identifier for this executor."""
        return "webScraping"
