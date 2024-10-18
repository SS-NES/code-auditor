"""Python packaging analyser module."""
from pathlib import Path

from . import Analyser, AnalyserType, Report, ReportStatus

import logging
logger = logging.getLogger(__name__)


class PackagingPython(Analyser):
    @staticmethod
    def get_type() -> AnalyserType:
        """Returns analyser type."""
        return AnalyserType.PACKAGING


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be included in the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return [
            '/pyproject.toml',
            '/setup.py',
            '/setup.cfg'
        ]


    @classmethod
    def analyse_file(cls, path: Path, report: Report) -> dict:
        """Analyses a file.

        Args:
            path (Path): Path of the file.
            report (Report): Analysis report.

        Returns:
            Dictionary of the analysis result of the file.
        """
        if path.name == 'pyproject.toml':
            pass

        elif path.name == 'setup.py':
            pass

        elif path.name == 'setup.cfg':
            pass
