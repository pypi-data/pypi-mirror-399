"""Models for streaming messages."""

import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class StreamType(str, Enum):
    """Type of stream message."""

    RESPONSE_CHUNK = "responseChunk"
    RESPONSE_DATA = "responseData"


class StreamDataType(str, Enum):
    """Type of content in stream message."""

    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    CODE = "code"
    JSON = "json"
    TABLE = "table"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILES = "files"
    CHART = "chart"
    MERMAID = "mermaid"
    MAP = "map"
    SEARCH = "search"
    TOOL_USE = "toolUse"
    OPEN_TAB = "openTab"
    MCP_UI = "mcpUi"
    WIDGET = "widget"
    ERROR = "error"
    INLINE_OPEN = "inlineOpen"
    INLINE_COLLAPSE = "inlineCollapse"
    AI_MESSAGE = "AIMessage"


@dataclass
class StreamDataContent:
    """Content structure for stream data.

    Note: For flexibility, stream messages can also use plain dicts instead of this dataclass
    to support arbitrary extra fields like 'language', 'meta', etc.
    """

    content: str | dict[str, Any] | list[Any]
    language: str | None = None


@dataclass
class ToolUseContentNested:
    """Inner nested content for tool use messages."""

    dataType: str
    data: dict[str, Any]


@dataclass
class ToolUseContent:
    """Content structure for tool use messages with proper nesting."""

    toolName: str
    toolIcon: str
    mainTask: str
    input: list[str]
    content: ToolUseContentNested
    meta: dict[str, Any] | None = None


@dataclass
class InlineContentNested:
    """Inner nested content for inline messages."""

    toolName: str
    toolIcon: str
    task: str
    mainTask: str
    content: str
    status: str


@dataclass
class InlineContent:
    """Content structure for inline messages with proper nesting."""

    blockId: int
    content: InlineContentNested


@dataclass
class SearchContent:
    """Content structure for search results."""

    query: str
    results: list[dict[str, Any]]


@dataclass
class StreamSource:
    """Source attribution for stream message."""

    name: str
    url: str


@dataclass
class StreamMessage:
    """Complete stream message structure."""

    type: StreamType
    dataType: StreamDataType
    data: StreamDataContent | ToolUseContent | InlineContent | SearchContent | dict[str, Any]
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    sources: list[StreamSource] | None = None
    close: bool = False
    error: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)

        # Convert enums to their values and remove None values
        def convert_value(value):
            if isinstance(value, Enum):
                return value.value
            elif isinstance(value, dict):
                return {k: convert_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [convert_value(item) for item in value]
            return value

        converted = {k: convert_value(v) for k, v in result.items() if v is not None}
        return converted
