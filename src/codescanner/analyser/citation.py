"""Citation analyser module."""
import yaml
from pathlib import Path

from . import Analyser, AnalyserType
from ..report import Report


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
    """Citation analyser class."""

    @classmethod
    def get_type(cls) -> AnalyserType:
        """Returns analyser type."""
        return AnalyserType.CITATION


    @classmethod
    def get_name(cls) -> str:
        """Returns analyser name."""
        return "Citation"


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
    def analyse_file(cls, path: Path, report: Report) -> dict:
        """Analyses a citation file.

        Args:
            path (Path): Path of the citation file.
            report (Report): Analysis report.

        Returns:
            Dictionary of the analysis results.
        """
        # Read citation file
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = yaml.safe_load(file)

        except:
            report.add_issue(cls, "Invalid citation file.", path)
            return {}

        # Check if title is missing
        if 'title' not in content:
            report.add_issue(cls, "The citation file is missing the title.", path)

        # Check if authors are missing
        if 'authors' not in content:
            report.add_issue(cls, "The citation file is missing the authors.", path)

        # Check if type of work is indicated different from software (e.g. dataset)
        if content.get('type') and content['type'] != 'software':
            report.add_issue(cls, "The type of work is not indicated as software.", path)

        # Set metadata
        keys = {
            'abstract': 'description',
            'date-released': 'date_released',
            'doi': 'doi',
            'keywords': 'keywords',
            'repository-code': 'repository_code',
            'title': 'name',
            'version': 'version',
        }
        for key, metadata_key in keys.items():
            report.add_metadata(cls, metadata_key, content.get(key), path)


    @classmethod
    def analyse_results(cls, results: dict, report: Report):
        """Analyses the analysis results of the files.

        Args:
            results (dict): Analysis results of the files.
            report (Report): Analysis report.
        """
        if len(results) > 1:
            report.add_issue(cls, "Multiple citation files found.")
