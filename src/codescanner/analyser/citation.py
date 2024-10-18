"""Citation analyser module."""
import yaml
from pathlib import Path

from . import Analyser, AnalyserType, Report, ReportStatus


VALID_ATTRS = [
    'abstract',
    'authors',
    'cff-version',
    'commit',
    'contact',
    'date-released',
    'doi',
    'identifiers',
    'keywords',
    'license',
    'license-url',
    'message',
    'preferred-citation',
    'references',
    'repository',
    'repository-artifact',
    'repository-code',
    'title',
    'type',
    'url',
    'version',
]


class Citation(Analyser):
    @staticmethod
    def get_type() -> AnalyserType:
        """Returns analyser type."""
        return AnalyserType.CITATION


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be included in the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return [
            '/*.cff',
        ]


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
        if len(files) > 1:
            report.invalids.append("Multiple citation files found.")

        for path in files:
            with open(root / path, 'r', encoding='utf-8') as file:
                content = yaml.safe_load(file)
