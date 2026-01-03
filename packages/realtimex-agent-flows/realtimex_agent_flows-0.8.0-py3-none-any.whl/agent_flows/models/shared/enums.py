from enum import Enum


class HttpMethod(str, Enum):
    """Supported HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class BodyType(str, Enum):
    """Supported request body formats."""

    JSON = "json"
    FORM_URLENCODED = "form_urlencoded"
    FORM_MULTIPART = "form_multipart"
    TEXT = "text"
    RAW = "raw"


class CaptureMode(str, Enum):
    """Data extraction modes for web scraping."""

    TEXT = "text"
    HTML = "html"
    QUERYSELECTOR = "querySelector"


class ResponseFormat(str, Enum):
    """Supported LLM response formats."""

    TEXT = "text"
    JSON = "json"
    JSON_SCHEMA = "json_schema"
    WIDGET = "widget"


class ComparisonOperator(str, Enum):
    """Supported comparison operators."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"


class MCPProvider(str, Enum):
    """Provider types for MCP server actions."""

    REMOTE = "remote"
    LOCAL = "local"


class ConditionType(str, Enum):
    """Supported types for condition comparison."""

    AUTO = "auto"
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"


class LoopType(str, Enum):
    """Loop execution patterns."""

    FOR = "for"
    WHILE = "while"
    FOR_EACH = "forEach"


class Combinator(str, Enum):
    """Logical combinators for condition groups."""

    AND = "and"
    OR = "or"
    NOT = "not"


class SearchProvider(str, Enum):
    """Supported web search providers."""

    GOOGLE = "google"
    BING = "bing"
    DUCKDUCKGO = "duckduckgo"
    SERPAPI = "serpapi"
    SERPLY = "serply"
    SEARXNG = "searxng"
    TAVILY = "tavily"


class SearchType(str, Enum):
    """Supported search types."""

    SEARCH = "search"
    NEWS = "news"


class ExtractionMode(str, Enum):
    """Content extraction modes for web scraping."""

    MARKDOWN = "markdown"
    HTML = "html"
    SCHEMA = "schema"
    LLM = "llm"


class HtmlVariant(str, Enum):
    """HTML extraction variants."""

    CLEAN = "clean"
    RAW = "raw"


class SchemaFieldType(str, Enum):
    """Schema field extraction types."""

    TEXT = "text"
    ATTRIBUTE = "attribute"
    HTML = "html"


class VariableType(str, Enum):
    """Supported types for variable assignment."""

    AUTO = "auto"
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"


class UserAgentMode(str, Enum):
    """User agent configuration modes."""

    DEFAULT = "default"
    RANDOM = "random"


__all__ = [
    "HttpMethod",
    "BodyType",
    "CaptureMode",
    "ResponseFormat",
    "ComparisonOperator",
    "MCPProvider",
    "LoopType",
    "Combinator",
    "SearchProvider",
    "SearchType",
    "ExtractionMode",
    "HtmlVariant",
    "SchemaFieldType",
    "UserAgentMode",
    "ConditionType",
    "VariableType",
]
