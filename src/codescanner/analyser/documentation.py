"""Documentation analyser module."""
from pathlib import Path

from . import Analyser
from ..processor import ProcessorType
from ..report import Report


class Documentation(Analyser):
    """Documentation analyser class."""

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
            '/readme',
            '/readme.*',
        ]


    @classmethod
    def analyse_content(cls, content: str, report: Report, path: Path=None) -> dict:
        """Analyses content.

        Args:
            content (str): Content.
            report (Report): Analysis report.
            path (Path): Path of the content file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        pass


    @classmethod
    def analyse_file(cls, path: Path, report: Report) -> dict:
        """Analyses a documentation file.

        Args:
            path (Path): Path of the documentation file.
            report (Report): Analyse report.

        Returns:
            Dictionary of the analysis results.
        """
        report.metadata.add(cls, 'readme_file', path.relative_to(report.path), path)
        return super().analyse_file(path, report)
