"""Analysis report module."""
from pathlib import Path

from .utils import get_id


class Report:
    """Analysis report class."""

    def __init__(self):
        """Initializes analysis report object."""
        self.issues = []
        self.metadata = {}


    def _get_source(self, analyser, src=None):
        if isinstance(src, Path):
            src = src.as_posix()

        return get_id(analyser) + ((':' + src) if src else '')


    def add_metadata(self, analyser, key: str, val, src=None):
        """Sets metadata attribute.

        Args:
            analyser (Analyser): Analyser class.
            key (str): Metadata attribute key.
            val: Metadata attribute value.
            src: Metadata attribute source (optional).
        """
        if key not in self.metadata:
            self.metadata[key] = []
        self.metadata[key].append((val, self._get_source(analyser, src)))


    def add_issue(self, analyser, msg: str, src=None):
        """Sets issue message.

        Args:
            analyser (Analyser): Analyser class.
            msg (str): Invalid message.
            src: Metadata attribute source (optional).
        """
        self.issues.append((msg, self._get_source(analyser, src)))
