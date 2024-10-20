"""Rule module."""
from dataclasses import dataclass
import fnmatch


def _is_pattern(val: str) -> bool:
    """Checks if rule value is a pattern."""
    return ('*' in val) or ('?' in val) or ('[' in val)


def _is_nested(val: str) -> bool:
    """Checks if rule value is nested."""
    return ('/' in val)


@dataclass(init=False)
class Rule:
    """Rule class."""

    val: str
    is_dir: bool
    is_pattern: bool
    is_nested: bool
    analysers: list[str]


    def __init__(self, val: str, analyser: str = None):
        self.is_dir = val[-1] == '/'
        if self.is_dir:
            val = val[:-1]
        self.is_nested = val[0] == '/'
        if self.is_nested:
            val = val[1:]
        else:
            self.is_nested = _is_nested(val)
        self.is_pattern = _is_pattern(val)
        self.val = val
        self.analysers = [analyser] if analyser else []


    def match(self, val: str) -> bool:
        return fnmatch.fnmatch(val, self.val)