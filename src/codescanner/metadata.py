"""Metadata module."""
from __future__ import annotations

class Metadata:
    """Metadata class."""

    def __init__(self):
        """Initializes metadata object."""
        self._data = {}


    def set(self, key: str, val, src):
        """Sets metadata attribute.

        Args:
            key (str): Metadata attribute key.
            val: Metadata attribute value.
            src: Metadata source.
        """
        if not val:
            return
        if key not in self._data:
            self._data[key] = []
        self._data[key].append((src, val))


    def get(self, key: str, src: None):
        """Returns metadata attribute value.

        Args:
            key (str): Metadata attribute key.
            src: Metadata source (optional)

        Returns:
            Metadata attribute value.
        """
        items = self._data.get(key, {})
        if not src:
            items
        for item in items:
            if item[0] == src:
                return val


    def merge(self, metadata: Metadata):
        """Merges metadata attributes.

        Args:
            metadata (Metadata): Metadata to be merged.
        """
        for key, items in metadata:
            if key not in self._data:
                self._data[key] = []
            self._data[key].extend(items)

