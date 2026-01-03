"""Production-ready structured logging for Agent Flows."""
# ruff: noqa: ARG001

import logging
import logging.config
from contextlib import contextmanager
from typing import Any
from urllib.parse import urlparse, urlunparse

import structlog

# Global flag to prevent multiple logging configurations
_LOGGING_CONFIGURED = False


class SensitiveDataSanitizer:
    """
    A comprehensive, recursive utility to sanitize sensitive data in any object.
    It sanitizes dictionary keys and sensitive patterns in URLs.
    """

    DEFAULT_SENSITIVE_KEYS = {
        "api_key",
        "apikey",
        "password",
        "passwd",
        "pwd",
        "token",
        "secret",
        "auth",
        "authorization",
        "credential",
        "cred",
        "key",
        "private",
        "sensitive",
    }

    def __init__(self, sensitive_keys: set[str] | None = None):
        """Initialize with custom sensitive keys."""
        self.sensitive_keys = sensitive_keys or self.DEFAULT_SENSITIVE_KEYS

    def sanitize(self, data: Any) -> Any:
        """
        Recursively sanitizes sensitive data. This is the main entry point.
        """
        if isinstance(data, dict):
            return self._sanitize_dict(data)
        if isinstance(data, list):
            return [self.sanitize(item) for item in data]
        if isinstance(data, str):
            # Only process strings that look like potential URLs to optimize
            if "://" in data and len(data) < 2048:  # Basic heuristic
                return self._sanitize_url(data)
            return data
        return data

    def _sanitize_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Sanitizes a dictionary by checking keys first, then recursively sanitizing values."""
        masked = {}
        for key, value in data.items():
            # First, check if the key is sensitive.
            if any(sensitive in key.lower() for sensitive in self.sensitive_keys):
                masked[key] = "***MASKED***"
            # Only if the key is NOT sensitive, recurse into the value.
            else:
                masked[key] = self.sanitize(value)
        return masked

    def _sanitize_url(self, url: str) -> str:
        """Sanitizes sensitive information in a URL."""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return url  # Not a valid URL

            netloc = parsed.netloc
            if "@" in netloc:
                netloc = f"[MASKED_CREDENTIALS]@{netloc.split('@', 1)[1]}"

            query = (
                "&".join(
                    f"{param.split('=', 1)[0]}=***MASKED***"
                    if any(sensitive in param.lower() for sensitive in self.sensitive_keys)
                    else param
                    for param in parsed.query.split("&")
                )
                if parsed.query
                else parsed.query
            )

            return urlunparse(
                (parsed.scheme, netloc, parsed.path, parsed.params, query, parsed.fragment)
            )
        except Exception:
            return "[MASKED_URL]"


def _sanitize_processor(sanitizer: SensitiveDataSanitizer):
    """Create a structlog processor that recursively sanitizes the entire event dictionary."""

    def processor(logger: Any, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
        return sanitizer.sanitize(event_dict)

    return processor


def setup_logging(
    level: str = "INFO",
    json_format: bool = True,
    enable_console: bool = True,
    output_file: str | None = None,
    sensitive_keys: set[str] | None = None,
) -> None:
    """Set up production-ready structured logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON format (True) or human-readable format (False)
        enable_console: Whether to enable console output
        output_file: Optional file path for log output
        sensitive_keys: Custom set of sensitive keys to mask (extends defaults)

    Note:
        This function should be called once at application startup.
        Subsequent calls will be ignored to prevent configuration conflicts.
    """
    global _LOGGING_CONFIGURED  # noqa: PLW0603
    if _LOGGING_CONFIGURED:
        return

    # Initialize sensitive data sanitizer
    if sensitive_keys:
        all_sensitive_keys = SensitiveDataSanitizer.DEFAULT_SENSITIVE_KEYS | sensitive_keys
        sanitizer = SensitiveDataSanitizer(all_sensitive_keys)
    else:
        sanitizer = SensitiveDataSanitizer()

    if json_format:
        # JSON format: Use structlog with ProcessorFormatter for clean JSON output
        handlers = {}
        if enable_console:
            handlers["console"] = {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "json",
                "stream": "ext://sys.stderr",
            }

        if output_file:
            handlers["file"] = {
                "class": "logging.FileHandler",
                "level": level,
                "formatter": "json",
                "filename": output_file,
                "encoding": "utf-8",
            }

        if not handlers:
            handlers["null"] = {"class": "logging.NullHandler"}

        # Configure logging with ProcessorFormatter for JSON
        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "json": {
                        "()": structlog.stdlib.ProcessorFormatter,
                        "foreign_pre_chain": [
                            structlog.contextvars.merge_contextvars,
                            structlog.stdlib.add_logger_name,
                            structlog.stdlib.add_log_level,
                            structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                            structlog.processors.StackInfoRenderer(),
                            structlog.processors.format_exc_info,
                            _sanitize_processor(sanitizer),
                            _normalize_execution_time,
                        ],
                        "processors": [
                            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                            structlog.processors.EventRenamer(to="message"),
                            _group_extra_attributes,
                            structlog.processors.JSONRenderer(ensure_ascii=False),
                        ],
                    },
                },
                "handlers": handlers,
                "root": {
                    "handlers": list(handlers.keys()),
                    "level": level,
                },
            }
        )

        # Configure structlog for JSON mode
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.contextvars.merge_contextvars,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                _sanitize_processor(sanitizer),
                _normalize_execution_time,
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    else:
        # Human-readable format: Use structlog's dev console renderer
        handlers = {}
        if enable_console:
            handlers["console"] = {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "plain",
                "stream": "ext://sys.stderr",
            }

        if output_file:
            handlers["file"] = {
                "class": "logging.FileHandler",
                "level": level,
                "formatter": "plain",
                "filename": output_file,
                "encoding": "utf-8",
            }

        if not handlers:
            handlers["null"] = {"class": "logging.NullHandler"}

        # Configure logging with simple formatter for human-readable output
        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "plain": {
                        "()": structlog.stdlib.ProcessorFormatter,
                        "foreign_pre_chain": [
                            structlog.contextvars.merge_contextvars,
                            structlog.stdlib.add_logger_name,
                            structlog.stdlib.add_log_level,
                            structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                            _sanitize_processor(sanitizer),
                            _normalize_execution_time,
                        ],
                        "processors": [
                            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                            structlog.dev.ConsoleRenderer(
                                colors=True,
                                exception_formatter=structlog.dev.RichTracebackFormatter(
                                    show_locals=False
                                ),
                            ),
                        ],
                    },
                },
                "handlers": handlers,
                "root": {
                    "handlers": list(handlers.keys()),
                    "level": level,
                },
            }
        )

        # Configure structlog for human-readable mode
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.contextvars.merge_contextvars,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                _sanitize_processor(sanitizer),
                _normalize_execution_time,
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    _LOGGING_CONFIGURED = True


def _normalize_execution_time(
    logger: Any,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Convert execution_time (seconds) to duration_ms (milliseconds)."""
    if "execution_time" in event_dict:
        execution_time = event_dict.pop("execution_time")
        if isinstance(execution_time, int | float):
            event_dict["duration_ms"] = round(execution_time * 1000)
    return event_dict


def _group_extra_attributes(
    logger: Any,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Group all non-reserved fields under 'attrs' and ensure consistent field ordering."""
    # Reserved fields that should stay at top level in specific order
    reserved_fields = {
        "timestamp",
        "level",
        "logger",
        "message",
        "flow_id",
        "step_id",
        "step_type",
        "step_index",
        "duration_ms",
        # Keep exception info top-level
        "exc_info",
        "stack_info",
        "exception",
        # Prevent nesting attrs into attrs
        "attrs",
        "_record",
        "_from_structlog",
    }

    # Create ordered result with consistent field ordering
    ordered_result = {}

    # Add fields in specific order
    field_order = [
        "timestamp",
        "level",
        "logger",
        "message",
        "flow_id",
        "step_id",
        "step_index",
        "step_type",
        "duration_ms",
    ]

    for field in field_order:
        if field in event_dict:
            ordered_result[field] = event_dict[field]

    # Collect non-reserved keys for attrs
    attrs = {k: v for k, v in event_dict.items() if k not in reserved_fields}

    # Add attrs if not empty
    if attrs:
        ordered_result["attrs"] = attrs

    # Add exception info at the end if present
    if "exception" in event_dict:
        ordered_result["exception"] = event_dict["exception"]

    return ordered_result


@contextmanager
def execution_context(
    flow_id: str,
    step_id: str | None = None,
    step_index: int | None = None,
    step_type: str | None = None,
    **extra_context,
):
    """Context manager for binding execution context to all logs within the block.

    Args:
        flow_id: Flow identifier
        step_id: Current step ID
        step_index: Current step index
        step_type: Current step type
        **extra_context: Additional context fields

    Yields:
        Structured logger with context automatically bound

    Example:
        with execution_context("flow-123", step_id="step-1", step_type="api_call"):
            log = get_logger()
            log.info("Starting API call")  # Automatically includes flow_id, step_id, etc.
    """
    # Bind context using structlog's contextvars
    context = {
        "flow_id": flow_id,
        "step_id": step_id,
        "step_index": step_index,
        "step_type": step_type,
        **extra_context,
    }

    # Filter out None values
    context = {k: v for k, v in context.items() if v is not None}

    structlog.contextvars.bind_contextvars(**context)

    try:
        yield get_logger()
    finally:
        # Unbind the context
        structlog.contextvars.unbind_contextvars(*context.keys())


def get_logger(name: str = "agent_flows") -> structlog.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (defaults to 'agent_flows')

    Returns:
        Structured logger with context binding support

    Example:
        log = get_logger()
        log.info("Flow started", flow_name="my-flow")

        # With context:
        with execution_context("flow-123"):
            log.info("Step completed")  # Automatically includes flow_id
    """
    return structlog.get_logger(name)
