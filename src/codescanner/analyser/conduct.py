"""Code of conduct analyser module."""
from pathlib import Path

from . import Analyser, AnalyserType
from ..report import Report


class Conduct(Analyser):
    """Code of conduct analyser class."""

    @classmethod
    def get_type(cls) -> AnalyserType:
        """Returns analyser type."""
        return AnalyserType.COMMUNITY


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
        ]


    @classmethod
    def analyse_content(cls, content: str, report: Report, path: Path=None) -> dict:
        """Analyses code of conduct content.

        Args:
            content (str): Code of conduct content.
            report (Report): Analysis report.
            path (Path): Path of the content file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        if path:
            report.metadata.add(cls, 'conduct_file', path.relative_to(report.path), path)
