"""Jupyter notebooks analyser module."""
from pathlib import Path

from . import Analyser, AnalyserType
from ..report import Report


class CodeJupyter(Analyser):
    """Jupyter notebooks analyser class."""

    @classmethod
    def get_type(cls) -> AnalyserType:
        """Returns analyser type."""
        return AnalyserType.CODE


    @classmethod
    def get_name(cls) -> str:
        """Returns analyser name."""
        return "Jupyter Notebooks"


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be included in the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return [
            '*.ipynb',
        ]


    @classmethod
    def excludes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be excluded from the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return [
            '.ipynb_checkpoints/',
        ]


    @classmethod
    def analyse_file(cls, path: Path, report: Report) -> dict:
        """Analyses a Jupyter notebook file.

        Args:
            path (Path): Path of the Jupyter notebook file.
            report (Report): Analysis report.

        Returns:
            Dictionary of the analysis results.
        """
        raise NotImplementedError