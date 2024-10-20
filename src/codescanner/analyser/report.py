"""Analyser report module."""
from enum import Enum
from pathlib import Path

from ..metadata import Metadata
from ..utils import get_id


class Report:
    """Analyser report class."""

    def __init__(self, analyser):
        """Initializes analyser report object.

        Args:
            analyser: Analyser class.
        """
        self._analyser = analyser
        self._analyser_id = get_id(analyser)
        self.results = {}
        self.invalids = []
        self.metadata = Metadata()


    def _get_source(self, src=None):
        if isinstance(src, Path):
            src = src.as_posix()

        return self._analyser_id + ((':' + src) if src else '')


    def set_results(self, results: dict):
        self.results = results


    def set_metadata(self, key:str, val, src=None):
        """Sets metadata attribute.

        Args:
            key (str): Metadata attribute key.
            val: Metadata attribute value.
            src (str): Metadata attribute source (optional).
        """
        self.metadata.set(key, val, self._get_source(src))


    def set_invalid(self, msg: str, src=None):
        self.invalids.append((msg, self._get_source(src)))
