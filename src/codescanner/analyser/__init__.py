"""Analyser module."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from enum import Enum

from ..report import Report

import logging
logger = logging.getLogger(__name__)


class AnalyserType(Enum):
    """Analyser type."""
    CODE = "Code"
    LICENSE = "License"
    CITATION = "Citation"
    VERSION_CONTROL = "Version Control"
    DOCUMENTATION = "Documentation"
    PACKAGING = "Packaging"
    REPOSITORY = "Repository"


class Analyser(ABC):
    """Analyse abstract class."""

    @classmethod
    @abstractmethod
    def get_type(cls) -> AnalyserType:
        """Returns analyser type."""
        raise NotImplementedError


    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """Returns analyser name."""
        raise NotImplementedError


    @classmethod
    @abstractmethod
    def includes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be included in the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        raise NotImplementedError


    @classmethod
    def excludes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be excluded from the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return []


    @classmethod
    def analyse_results(cls, results: dict, report: Report):
        """Analyses the analysis results of the files.

        Args:
            results (dict): Analysis results of the files.
            report (Report): Analysis report.
        """
        pass


    @classmethod
    @abstractmethod
    def analyse_file(cls, path: Path, report: Report) -> dict:
        """Analyses a file.

        Args:
            path (Path): Path of the file.
            report (Report): Analysis report.

        Returns:
            Dictionary of the analysis results.
        """
        raise NotImplementedError


    @classmethod
    def analyse(cls, root: Path, files: list[Path], report: Report) -> dict:
        """Performs the analysis of the files.

        Args:
            root (Path): Path of the code base.
            files (list[Path]): Paths of the files relative to the root path.
            report (Report): Analysis report.

        Returns:
            Dictionary of the analysis results of the files.
        """
        results = {}

        for path in files:
            logger.debug(f"Analysing `{path}`.")
            try:
                results[path.as_posix()] = cls.analyse_file(root / path, report)

            except NotImplementedError:
                logger.debug(f"{cls} file analyser is not implemented.")
                continue

        cls.analyse_results(results, report)

        return results


    @classmethod
    def output_results(cls, results: dict) -> str:
        pass
