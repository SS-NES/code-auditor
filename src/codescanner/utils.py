"""Utilities module."""
import re
from enum import Enum


"""Snake case conversion regular expression."""
REGEXP_SNAKE_CASE = re.compile(r'(?<!^)(?=[A-Z])')


class MessageType(Enum):
    """Message type."""
    INFO = 1
    # Informational only, no action required.
    SUGGESTION = 2
    # A recommended improvement for better code quality.
    NOTICE = 3
    # Something noteworthy but not necessarily problematic.
    WARNING = 4
    # A potential issue that should be addressed.
    ISSUE = 5
    # A problem that needs to be fixed.


class OutputType(Enum):
    """Output type."""
    PLAIN = 'plain'
    HTML = 'html'
    JSON = 'json'
    YAML = 'yaml'
    MARKDOWN = 'md'
    RST = 'rst'
    RTF = 'rtf'
    DOCX = 'docx'


def get_id(cls) -> str:
    """Returns snake-case class id."""
    return REGEXP_SNAKE_CASE.sub('_', cls.__qualname__).lower()
