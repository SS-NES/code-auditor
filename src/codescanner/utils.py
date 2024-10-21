"""Utilities module."""
import re
from enum import Enum


"""Snake case conversion regular expression."""
REGEXP_SNAKE_CASE = re.compile(r'(?<!^)(?=[A-Z])')


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
