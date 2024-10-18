"""Analyser module."""
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field

import logging
logger = logging.getLogger(__name__)


class AnalyserType(Enum):
    """Analyser type."""
    CODE = 1
    VERSION_CONTROL = 2
    DOCUMENTATION = 3
    LICENSE = 4
    CITATION = 5
    REPOSITORY = 6
    PACKAGING = 7
    CONTINUOUS_INTEGRATION = 8


class ReportStatus(Enum):
    """Analysis report status."""
    MISSING = 0
    EXISTS = 1


@dataclass
class Report:
    """Analysis report."""
    status: ReportStatus=ReportStatus.MISSING
    files: dict=field(default_factory=lambda: {})
    invalids: list=field(default_factory=lambda: [])
    metadata: dict=field(default_factory=lambda: {})


class Analyser(ABC):
    """Analyse abstract class."""

    @staticmethod
    @abstractmethod
    def get_type() -> AnalyserType:
        """Returns analyser type."""
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
    @abstractmethod
    def analyse_file(cls, path: Path, report: Report) -> dict:
        """Analyses a file.

        Args:
            path (Path): Path of the file.
            report (Report): Analysis report.

        Returns:
            Dictionary of the analysis result of the file.
        """
        raise NotImplementedError


    @classmethod
    def analyse_files(cls, root: Path, files: list[Path], report: Report) -> dict:
        """Analyses a set of files.

        Args:
            root (Path): Path of the code base.
            files (list[Path]): Paths of the files.
            report (Report): Analysis report.

        Returns:
            Dictionary of the analysis results of the files.
        """
        results = {}

        for path in files:
            logger.debug(f"Analysing `{path}`.")

            result = cls.analyse_file(root / path, report)
            if result is not None:
                results[path.as_posix()] = result

        return results


    @classmethod
    def analyse(cls, root: Path, files: list[Path]) -> Report:
        """Performs the analysis.

        Args:
            root (Path): Path of the code base.
            files (list[Path]): Paths of the files.

        Returns:
            Analysis result.
        """
        if not files:
            return Report()

        report = Report(status=ReportStatus.EXISTS)
        result = cls.analyse_files(root, files, report)
        if result:
            report.files = result

        return report
