"""Utilities module."""
import re
from enum import Enum


"""Snake case conversion regular expression."""
REGEXP_SNAKE_CASE = re.compile(r'(?<!^)(?=[A-Z])')


class MessageType(Enum):
    """Message type."""
    INFO = 1
    """Informational only, no action required."""
    SUGGESTION = 2
    """A recommended improvement for better code quality."""
    NOTICE = 3
    """Something noteworthy but not necessarily problematic."""
    WARNING = 4
    """A potential issue that should be addressed."""
    ISSUE = 5
    """A problem that needs to be fixed."""


class OutputType(Enum):
    """Output type."""
    PLAIN = 'plain'
    """Plain text"""
    HTML = 'html'
    """HTML"""
    JSON = 'json'
    """JSON"""
    YAML = 'yaml'
    """YAML"""
    MARKDOWN = 'markdown'
    """Markdown"""
    RST = 'rst'
    """reStructuredText"""
    RTF = 'rtf'
    """Rich text format"""
    DOCX = 'docx'
    """Office Open XML"""


def get_class_name(cls) -> str:
    """Returns snake-case class name."""
    return REGEXP_SNAKE_CASE.sub('_', cls.__qualname__).lower()
