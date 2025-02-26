"""Code analyser module."""
import functools
from abc import ABC, abstractmethod
from pathlib import Path
from typing import final

from . import Analyser, AnalyserType
from .. import get_analysers
from ..report import Report


class Code(Analyser):
    """Code analyser class."""

    @classmethod
    @final
    def get_type(cls) -> AnalyserType:
        """Returns analyser type."""
        return AnalyserType.CODE


    @classmethod
    @abstractmethod
    def get_languages(cls) -> list[str]:
        """Returns list of languages supported by the analyser."""
        raise NotImplementedError


    @classmethod
    @functools.cache
    def get_analysers(cls, lang: str) -> list[Analyser]:
        """Returns analysers for the specified language.

        Args:
            lang (str): Language.

        Returns:
            List of analysers.
        """
        return [
            analyser for analyser in get_analysers()
            if lang in analyser.get_languages()
        ]
