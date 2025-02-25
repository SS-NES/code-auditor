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
    def analyse_content(cls, content: str, report: Report, path: Path=None) -> dict:
        """Analyses a code content.

        Args:
            content (str): Code content.
            report (Report): Analysis report.
            path (Path): Path of the code file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        raise NotImplementedError


    @classmethod
    def analyse_file(cls, path: Path, report: Report) -> dict:
        """Analyses a code file.

        Args:
            path (Path): Path of the code file.
            report (Report): Analysis report.

        Returns:
            Dictionary of the analysis results.
        """
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()

        return cls.analyse_content(content, report, path)


    @classmethod
    @abstractmethod
    def get_languages(cls) -> list[str]:
        """Returns list of languages supported by the analyser."""
        raise NotImplementedError


    @staticmethod
    @functools.cache
    def get_analysers(lang: str) -> list[Analyser]:
        """Returns analysers for the specified language.

        Args:
            lang (str): Language

        Returns:
            List of analysers.
        """
        return [
            analyser for analyser in get_analysers()
            if lang in analyser.get_languages()
        ]
