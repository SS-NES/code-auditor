"""Change log analyser module."""
from pathlib import Path

from . import Analyser
from ..processor import ProcessorType
from ..report import Report


class ChangeLog(Analyser):
    """Change log analyser class."""

    @classmethod
    def get_type(cls) -> ProcessorType:
        """Returns analyser type."""
        return ProcessorType.DOCUMENTATION


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be included in the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return [
            '/changelog'
            '/changelog.*',
        ]


    @classmethod
    def analyse_content(cls, content: str, report: Report, path: Path=None) -> dict:
        """Analyses change log content.

        Args:
            content (str): Change log content.
            report (Report): Analysis report.
            path (Path): Path of the content file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        if path:
            report.metadata.add(cls, 'changelog_file', path.relative_to(report.path), path)
