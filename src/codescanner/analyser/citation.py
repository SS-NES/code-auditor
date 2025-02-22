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

        # Process attributes
        metadata_keys = {
            'abstract': 'description',
            'date-released': 'date_released',
            'doi': 'doi',
            'keywords': 'keywords',
            'repository-code': 'repository_code',
            'title': 'name',
            'version': 'version',
            'license': 'license',
        }

        for key, val in content.items():
            if key not in VALID_ATTRS:
                report.add_issue(cls, f"Invalid citation file attribute {key}", path)
                continue

            if key == 'type' and val != 'software':
                report.add_issue(cls, "The type of work is not indicated as software.", path)

            if key in metadata_keys:
                report.add_metadata(cls, metadata_keys[key], val, path)
