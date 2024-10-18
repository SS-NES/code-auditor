"""Git analyser module."""
from pathlib import Path

from . import Analyser, AnalyserType, Report, ReportStatus


class Git(Analyser):
    @staticmethod
    def get_type() -> AnalyserType:
        """Returns analyser type."""
        return AnalyserType.VERSION_CONTROL


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be included in the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return [
            '.git/',
        ]


    @classmethod
    def excludes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be excluded from the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        items = [
            '.git/'
        ]

        ignore_file = path / '.gitignore'
        if ignore_file.exists():
            with open(ignore_file, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line.startswith('#') and line.endswith('/'):
                        items.append(line)

        return items


    @classmethod
    def analyse_file(cls, path: Path, report: Report) -> dict:
        """Analyses a file.

        Args:
            path (Path): Path of the file.
            report (Report): Analysis report.

        Returns:
            Dictionary of the analysis result of the file.
        """
        report.metadata["version_control"] = "git"
