"""Community analyser module."""
import re
from pathlib import Path

from . import Analyser, AnalyserType
from ..report import Report


class Community(Analyser):
    """Community analyser class."""

    @classmethod
    def get_type(cls) -> AnalyserType:
        """Returns analyser type."""
        return AnalyserType.COMMUNITY


    @classmethod
    def get_name(cls) -> str:
        """Returns analyser name."""
        return "Community"


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be included in the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return [
            '/CONDUCT.*',
            '/CODE_OF_CONDUCT.*',
            '/CONTRIBUTING.*',
        ]


    @classmethod
    def analyse_content(cls, content: str, report: Report, path: Path=None) -> dict:
        """Analyses community-related content.

        Args:
            content (str): Communit-related content.
            report (Report): Analysis report.
            path (Path): Path of the content file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        if not path:
            return

        if re.search(r'CONTRIBUTING', path.name, re.IGNORECASE):
            report.add_notice(cls, "Contributing guidelines exists.", path)
            report.add_metadata(cls, 'contributing_file', path.relative_to(report.path), path)

        elif re.search(r'CONDUCT', path.name, re.IGNORECASE):
            report.add_notice(cls, "Code of conduct exists.", path)
            report.add_metadata(cls, 'conduct_file', path.relative_to(report.path), path)

