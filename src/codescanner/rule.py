"""Rule module."""
from dataclasses import dataclass
import fnmatch


@dataclass(init=False)
class Rule:
    """Rule class."""

    val: str
    is_dir: bool
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
            self.is_nested = '/' in val
        self.val = val
        self.analysers = [analyser] if analyser else []


    def match(self, val: str) -> bool:
        return fnmatch.fnmatch(val, self.val)
