"""Code analyser module."""
import functools
from abc import ABC, abstractmethod
from pathlib import Path
from typing import final

from . import Analyser
from .. import get_analysers
from ..processor import ProcessorType
from ..report import Report


class Code(Analyser):
    """Code analyser class."""

    @classmethod
    @final
    def get_type(cls) -> ProcessorType:
        """Returns analyser type."""
        return ProcessorType.CODE


    @classmethod
    @abstractmethod
    def get_language(cls) -> str:
        """Returns language supported by the analyser."""
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
            if hasattr(analyser, 'get_language') and lang == analyser.get_language()
        ]


    @classmethod
    @abstractmethod
    def analyse_code(cls, content: str, report: Report, path: Path=None) -> dict:
        """Analyses code content.

        Args:
            content (str): Code content.
            report (Report): Analysis report.
            path (Path): Path of the code file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        raise NotImplementedError


    @classmethod
    @final
    def analyse_content(cls, content: str, report: Report, path: Path=None) -> dict:
        """Analyses content.

        Results:
            num_lines (int): Number of lines.
            num_code_lines (int): Number non-empty lines.
            size (int): Size in bytes.

        Args:
            content (str): Content.
            report (Report): Analysis report.
            path (Path): Path of the file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        # Get code analysis result
        result = cls.analyse_code(content, report, path)
        if not result:
            result = {}

        # Set content size
        result['size'] = len(content)

        # Set number of lines
        lines = content.splitlines()
        result['num_lines'] = len(lines)

        # Set number of code lines
        code_lines = list(filter(lambda line: line.strip() != '', lines))
        result['num_code_lines'] = len(code_lines)

        return result


    @classmethod
    def output_result(cls, report: Report, result: dict) -> str:
        return ''
