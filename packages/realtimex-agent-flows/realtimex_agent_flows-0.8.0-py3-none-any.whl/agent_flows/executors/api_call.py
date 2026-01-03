"""ApiCallExecutor for HTTP requests."""

import asyncio
import json
import time
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import aiohttp
from pydantic import ValidationError
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from agent_flows.core.resources.interpolation import VariableInterpolator
from agent_flows.exceptions import ConfigurationError, ExecutorError
from agent_flows.executors.base import BaseExecutor
from agent_flows.models.credentials import CredentialType
from agent_flows.models.execution import ExecutionContext, ExecutorResult
from agent_flows.models.executors import ApiCallExecutorConfig
from agent_flows.models.shared import BodyType, FormDataDefinition, HeaderDefinition, HttpMethod
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class ApiCallExecutor(BaseExecutor):
    """Executor for API call steps."""

    def __init__(self) -> None:
        """Initialize the API call executor."""
        self.interpolator = VariableInterpolator()

    def get_required_fields(self) -> list[str]:
        """Get list of required configuration fields."""
        return ["url"]

    def get_optional_fields(self) -> list[str]:
        """Get list of optional configuration fields."""
        return [
            "method",
            "headers",
            "bodyType",
            "body",
            "formData",
            "responseVariable",
            "directOutput",
            "timeout",
            "maxRetries",
            "followRedirects",
        ]

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate API call configuration.

        Args:
            config: Step configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            ValidationError: If configuration is invalid (Pydantic validation)
            ConfigurationError: If configuration is invalid (other errors)
        """
        try:
            # Use Pydantic model for comprehensive validation
            ApiCallExecutorConfig(**config)
            return True

        except ValidationError:
            # Let ValidationError bubble up for better error formatting
            raise
        except Exception as e:
            raise ConfigurationError(
                f"API call executor configuration validation failed: {str(e)}"
            ) from e

    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Execute API call.

        Args:
            config: Step configuration containing API call parameters
            context: Execution context

        Returns:
            ExecutorResult with API response data

        Raises:
            ExecutorError: If API call fails
        """
        start_time = time.time()

        try:
            # First perform basic validation without URL validation (to allow template variables)
            basic_validated_config = self._validate_basic_config(config)

            # Perform variable interpolation on configuration
            interpolated_config = self._interpolate_config(
                basic_validated_config, context.variables
            )

            # Now validate the final interpolated configuration
            final_validated_config = ApiCallExecutorConfig(**interpolated_config)

            self._apply_credentials(final_validated_config, context)

            log.info(
                "Starting API call execution",
                method=final_validated_config.method.value,
                url=self._mask_sensitive_url(final_validated_config.url),
            )

            # Emit API call streaming update
            if context.step_execution_service.streaming_handler:
                masked_url = self._mask_sensitive_url(final_validated_config.url)
                content = f"Making {final_validated_config.method.value} request to {masked_url}"
                context.step_execution_service.streaming_handler.stream_step(
                    "API Call", "Globe", content, content
                )

            # Execute the API call with retry logic
            response_result = await self._execute_with_retries(final_validated_config, context)

            # Extract clean response data and metadata
            clean_response_data = response_result["response_data"]
            status_code = response_result["status_code"]
            response_headers = response_result["headers"]
            content_type = response_result["content_type"]

            # Determine variables to update
            variables_updated: dict[str, Any] = {}
            if final_validated_config.responseVariable:
                variables_updated[final_validated_config.responseVariable] = clean_response_data

            execution_time = time.time() - start_time

            log.info(
                "API call completed successfully",
                execution_time=execution_time,
                status_code=status_code,
            )

            return ExecutorResult(
                success=True,
                data=clean_response_data,  # Pure response data only
                variables_updated=variables_updated,
                direct_output=final_validated_config.directOutput,
                execution_time=execution_time,
                metadata={
                    "method": final_validated_config.method.value,
                    "url": self._mask_sensitive_url(final_validated_config.url),
                    "status_code": status_code,
                    "headers": response_headers,
                    "content_type": content_type,
                    "response_size": len(str(clean_response_data))
                    if clean_response_data is not None
                    else 0,
                    "step_id": context.step_id,
                    "step_type": "apiCall",
                },
            )

        except ConfigurationError:
            # Re-raise configuration errors as-is
            raise

        except Exception as e:
            # Wrap with executor-specific context for better error messages
            raise ExecutorError(f"API call execution failed: {str(e)}") from e

    def _validate_basic_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Perform basic validation without URL validation to allow template variables.

        Args:
            config: Raw configuration dictionary

        Returns:
            Validated configuration dictionary

        Raises:
            ConfigurationError: If basic validation fails
        """
        # Check required fields
        if "url" not in config:
            raise ConfigurationError("Missing required field: url")

        # Create a copy for validation
        validated_config = config.copy()

        # Set defaults for optional fields
        validated_config.setdefault("method", "GET")
        validated_config.setdefault("headers", [])
        validated_config.setdefault("bodyType", None)
        validated_config.setdefault("body", None)
        validated_config.setdefault("formData", [])
        validated_config.setdefault("responseVariable", None)
        validated_config.setdefault("directOutput", False)
        validated_config.setdefault("timeout", 30)
        validated_config.setdefault("maxRetries", 0)
        validated_config.setdefault("followRedirects", True)

        # Basic validation of non-URL fields
        try:
            # Validate method
            if validated_config["method"] not in [method.value for method in HttpMethod]:
                raise ValueError(f"Invalid HTTP method: {validated_config['method']}")

            # Validate timeout
            if not isinstance(validated_config["timeout"], int) or validated_config["timeout"] < 1:
                raise ValueError("Timeout must be a positive integer")

            # Validate maxRetries
            if (
                not isinstance(validated_config["maxRetries"], int)
                or validated_config["maxRetries"] < 0
            ):
                raise ValueError("Max retries must be a non-negative integer")

            # Validate headers format
            if not isinstance(validated_config["headers"], list):
                raise ValueError("Headers must be a list")

            # Validate formData format
            if not isinstance(validated_config["formData"], list):
                raise ValueError("Form data must be a list")

            # Validate body type
            if validated_config.get("bodyType"):
                body_type = validated_config["bodyType"]
                valid_body_types = [bt.value for bt in BodyType]
                if body_type not in valid_body_types:
                    raise ValueError(
                        f"Invalid body type: {body_type}. Must be one of: {valid_body_types}"
                    )

            # Validate JSON body if specified
            if validated_config.get("bodyType") == BodyType.JSON.value:
                body = validated_config.get("body")
                if body is None:
                    pass
                elif isinstance(body, str):
                    stripped_body = body.strip()
                    if stripped_body:
                        try:
                            json.loads(stripped_body)
                            validated_config["body"] = stripped_body
                        except json.JSONDecodeError as e:
                            raise ValueError(
                                f"Body must be valid JSON when bodyType is 'json': {str(e)}"
                            ) from e
                    else:
                        validated_config["body"] = None
                elif isinstance(body, dict | list):
                    # Already a JSON-serializable structure
                    pass
                else:
                    raise ValueError("Body must be a string, list, or dict when bodyType is 'json'")

            # Validate form data requirements
            if validated_config.get("bodyType") in [
                BodyType.FORM_URLENCODED.value,
                BodyType.FORM_MULTIPART.value,
            ] and not validated_config.get("formData"):
                raise ValueError(
                    f"Form data fields are required when bodyType is '{validated_config['bodyType']}'"
                )

        except ValueError as e:
            raise ConfigurationError(
                f"API call executor configuration validation failed: {str(e)}"
            ) from e

        return validated_config

    def _interpolate_config(
        self, config: dict[str, Any], variables: dict[str, Any]
    ) -> dict[str, Any]:
        """Perform variable interpolation on configuration.

        Args:
            config: Validated configuration dictionary
            variables: Variables for interpolation

        Returns:
            Configuration dictionary with interpolated values
        """
        # Create a copy to avoid modifying the original
        interpolated_config = config.copy()

        # Interpolate URL
        interpolated_config["url"] = self.interpolator.interpolate(config["url"], variables)

        # Interpolate headers
        interpolated_headers = []
        for header in config.get("headers", []):
            if isinstance(header, dict):
                interpolated_headers.append(
                    {
                        "key": self.interpolator.interpolate(header["key"], variables),
                        "value": self.interpolator.interpolate(header["value"], variables),
                    }
                )
            else:
                # Handle HeaderDefinition objects
                interpolated_headers.append(
                    {
                        "key": self.interpolator.interpolate(header.key, variables),
                        "value": self.interpolator.interpolate(header.value, variables),
                    }
                )
        interpolated_config["headers"] = interpolated_headers

        # Interpolate body
        body_value = config.get("body")
        if body_value is not None:
            if isinstance(body_value, str):
                interpolated_config["body"] = self.interpolator.interpolate(body_value, variables)
            else:
                interpolated_config["body"] = self.interpolator.interpolate_object(
                    body_value, variables
                )

        # Interpolate form data
        interpolated_form_data = []
        for form_field in config.get("formData", []):
            if isinstance(form_field, dict):
                interpolated_form_data.append(
                    {
                        "key": self.interpolator.interpolate(form_field["key"], variables),
                        "value": self.interpolator.interpolate(form_field["value"], variables),
                    }
                )
            else:
                # Handle FormDataDefinition objects
                interpolated_form_data.append(
                    {
                        "key": self.interpolator.interpolate(form_field.key, variables),
                        "value": self.interpolator.interpolate(form_field.value, variables),
                    }
                )
        interpolated_config["formData"] = interpolated_form_data

        return interpolated_config

    def _should_retry(self, exception: BaseException) -> bool:
        """Determine if a request should be retried based on the exception.

        Args:
            exception: The exception raised during the request.

        Returns:
            True if the request should be retried, False otherwise.
        """
        if isinstance(exception, aiohttp.ClientResponseError):
            # Do not retry on client-side errors (4xx)
            return exception.status >= 500
        # Retry on other client errors (e.g., network issues) and timeouts
        return isinstance(exception, aiohttp.ClientError | asyncio.TimeoutError)

    async def _execute_with_retries(
        self, config: ApiCallExecutorConfig, context: ExecutionContext
    ) -> Any:
        """Execute API call with retry logic.

        Args:
            config: Interpolated configuration
            context: Execution context

        Returns:
            Response data

        Raises:
            ExecutorError: If all retry attempts fail
        """
        if config.maxRetries == 0:
            # No retries, execute directly
            return await self._make_request(config, context)

        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(config.maxRetries + 1),
                wait=wait_exponential(multiplier=1, min=1, max=10),
                retry=retry_if_exception(self._should_retry),
                reraise=True,
            ):
                with attempt:
                    if attempt.retry_state.attempt_number > 1:
                        log.info(
                            "Retrying API call",
                            attempt=attempt.retry_state.attempt_number,
                            max_attempts=config.maxRetries + 1,
                        )

                    return await self._make_request(config, context)

        except RetryError as e:
            # Extract the original exception from the retry error
            original_error = e.last_attempt.exception()
            raise ExecutorError(
                f"API call failed after {config.maxRetries + 1} attempts: {str(original_error)}"
            ) from original_error

    async def _make_request(self, config: ApiCallExecutorConfig, _: ExecutionContext) -> Any:
        """Execute the actual HTTP request.

        Args:
            config: Interpolated configuration
            context: Execution context

        Returns:
            Response data

        Raises:
            aiohttp.ClientError: For HTTP client errors
            asyncio.TimeoutError: For timeout errors
        """
        # Build request headers
        headers = self._build_headers(config.headers)

        # Build request body and additional headers
        request_body, additional_headers = self._build_request_body(
            config.bodyType, config.body, config.formData
        )

        # Merge headers
        headers.update(additional_headers)

        # Create timeout configuration
        timeout = aiohttp.ClientTimeout(total=config.timeout)

        # Create connector with SSL settings
        connector = aiohttp.TCPConnector(
            ssl=True,  # Verify SSL certificates by default
            limit=100,  # Connection pool limit
            limit_per_host=30,  # Per-host connection limit
        )

        try:
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                auto_decompress=True,
            ) as session:
                log.debug(
                    "Making HTTP request",
                    method=config.method.value,
                    url=self._mask_sensitive_url(config.url),
                    headers=self._mask_sensitive_headers(headers),
                    body_size=len(str(request_body)) if request_body else 0,
                )

                async with session.request(
                    method=config.method.value,
                    url=config.url,
                    headers=headers,
                    data=request_body,
                    allow_redirects=config.followRedirects,
                ) as response:
                    # Read response content
                    response_text = await response.text()

                    log.debug(
                        "Received HTTP response",
                        status_code=response.status,
                        content_type=response.content_type,
                        content_length=len(response_text),
                    )

                    # Check for HTTP errors first
                    if response.status >= 400:
                        error_msg = f"HTTP {response.status}: {response.reason}"
                        if response_text:
                            error_msg += f" - {response_text[:200]}"
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=error_msg,
                        )

                    # Process response - keep only the pure response data
                    response_data = self._process_response(response, response_text)

                    # Return clean response data and metadata separately
                    return {
                        "response_data": response_data,
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "content_type": response.content_type,
                    }

        finally:
            # Ensure connector is properly closed
            if not connector.closed:
                await connector.close()

    def _build_headers(self, headers: list[HeaderDefinition]) -> dict[str, str]:
        """Convert header list to dictionary.

        Args:
            headers: List of header definitions

        Returns:
            Dictionary of headers
        """
        header_dict = {}
        for header in headers:
            header_dict[header.key] = header.value
        return header_dict

    def _build_request_body(  # noqa: PLR0911
        self,
        body_type: BodyType | None,
        body: Any,
        form_data: list[FormDataDefinition],
    ) -> tuple[Any, dict[str, str]]:
        """Build request body and additional headers.

        Args:
            body_type: Type of request body
            body: Body content (string or JSON-serializable structure)
            form_data: Form data fields

        Returns:
            Tuple of (request_body, additional_headers)
        """
        additional_headers = {}

        if not body_type:
            return None, additional_headers

        if body_type == BodyType.JSON:
            if body is None:
                return None, additional_headers

            try:
                if isinstance(body, dict | list):
                    request_body = json.dumps(body)
                elif isinstance(body, str):
                    stripped_body = body.strip()
                    if not stripped_body:
                        return None, additional_headers
                    parsed_json = json.loads(stripped_body)
                    request_body = json.dumps(parsed_json)
                else:
                    raise ValueError(
                        "JSON body must be a string, list, or dict when bodyType is 'json'"
                    )
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in request body: {str(e)}") from e

            additional_headers["Content-Type"] = "application/json"
            return request_body, additional_headers

        elif body_type == BodyType.FORM_URLENCODED:
            if form_data:
                # Convert form data to URL-encoded string
                form_dict = {field.key: field.value for field in form_data}
                request_body = urlencode(form_dict)
                additional_headers["Content-Type"] = "application/x-www-form-urlencoded"
                return request_body, additional_headers
            return None, additional_headers

        elif body_type == BodyType.FORM_MULTIPART:
            if form_data:
                # Create multipart form data
                # Note: Do NOT set Content-Type header manually - aiohttp's FormData
                # automatically generates the correct multipart/form-data header with boundary
                from aiohttp import FormData

                multipart_data = FormData(default_to_multipart=True)
                for field in form_data:
                    multipart_data.add_field(field.key, field.value)
                return multipart_data, additional_headers
            return None, additional_headers

        elif body_type == BodyType.TEXT:
            if body:
                additional_headers["Content-Type"] = "text/plain"
                return body, additional_headers
            return None, additional_headers

        elif body_type == BodyType.RAW:
            # Send body as-is without any processing
            return body, additional_headers

        return None, additional_headers

    def _process_response(self, response: aiohttp.ClientResponse, response_text: str) -> Any:
        """Process response based on content type.

        Args:
            response: HTTP response object
            response_text: Response text content

        Returns:
            Processed response data
        """
        content_type = response.content_type.lower() if response.content_type else ""

        # Try to parse as JSON if content type indicates JSON
        if "application/json" in content_type or "text/json" in content_type:
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, return as text
                log.warning(
                    "Failed to parse JSON response, returning as text",
                    content_type=content_type,
                )
                return response_text

        # For other content types, return as text
        return response_text

    def _mask_sensitive_url(self, url: str) -> str:
        """Mask sensitive information in URL for logging.

        Args:
            url: Original URL

        Returns:
            URL with sensitive parts masked
        """
        # Simple masking - replace query parameters that might contain sensitive data
        if "?" in url:
            base_url, query = url.split("?", 1)
            # Mask common sensitive parameter names
            sensitive_params = ["api_key", "apikey", "token", "password", "secret", "auth"]
            for param in sensitive_params:
                if param in query.lower():
                    return f"{base_url}?[MASKED_QUERY_PARAMS]"
            return url
        return url

    def _mask_sensitive_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Mask sensitive information in headers for logging.

        Args:
            headers: Original headers

        Returns:
            Headers with sensitive values masked
        """
        masked_headers = {}
        sensitive_header_names = {
            "authorization",
            "x-api-key",
            "x-auth-token",
            "cookie",
            "set-cookie",
            "x-access-token",
            "bearer",
        }

        for key, value in headers.items():
            if key.lower() in sensitive_header_names:
                masked_headers[key] = "[MASKED]"
            else:
                masked_headers[key] = value

        return masked_headers

    def get_step_type(self) -> str:
        """Return the step type identifier for this executor."""
        return "apiCall"

    def _apply_credentials(self, config: ApiCallExecutorConfig, context: ExecutionContext) -> None:
        """Inject credential payloads into the API request configuration."""
        credentials = getattr(context, "resolved_credentials", {})
        if not credentials:
            return

        for alias, bundle in credentials.items():
            if bundle.credential_type is CredentialType.HTTP_HEADER:
                name = bundle.payload["name"]
                value = bundle.payload["value"]
                self._merge_header(config, name, value)
                log.debug(
                    "Applied header credential",
                    credential_id=bundle.credential_id,
                    alias=alias,
                    header=name,
                )
            elif bundle.credential_type is CredentialType.QUERY_AUTH:
                name = bundle.payload["name"]
                value = bundle.payload["value"]
                config.url = self._append_query_param(config.url, name, value)
                log.debug(
                    "Applied query credential",
                    credential_id=bundle.credential_id,
                    alias=alias,
                    param=name,
                )
            elif bundle.credential_type is CredentialType.BASIC_AUTH:
                username = bundle.payload["username"]
                password = bundle.payload["password"]
                token = self._encode_basic_auth(username, password)
                self._merge_header(config, "Authorization", f"Basic {token}")
                log.debug(
                    "Applied basic auth credential",
                    credential_id=bundle.credential_id,
                    alias=alias,
                )
            # env_var does not apply to HTTP requests; ignore.

    def _merge_header(self, config: ApiCallExecutorConfig, name: str, value: str) -> None:
        """Replace or append a header on the request configuration."""
        headers: list[HeaderDefinition] = list(config.headers)
        lower_name = name.lower()
        for header in headers:
            if header.key.lower() == lower_name:
                header.value = value
                config.headers = headers
                return
        headers.append(HeaderDefinition(key=name, value=value))
        config.headers = headers

    def _append_query_param(self, url: str, name: str, value: str) -> str:
        """Append or replace a query parameter on the URL."""
        parsed = urlparse(url)
        query_items = [
            (k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if k != name
        ]
        query_items.append((name, value))
        new_query = urlencode(query_items)
        return urlunparse(parsed._replace(query=new_query))

    def _encode_basic_auth(self, username: str, password: str) -> str:
        from base64 import b64encode

        token = b64encode(f"{username}:{password}".encode())
        return token.decode("utf-8")
