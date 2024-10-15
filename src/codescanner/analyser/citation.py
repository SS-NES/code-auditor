"""Citation analyser module."""
import yaml
from pathlib import Path

from . import Analyser, AnalyserType

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
        return AnalyserType.CITATION


    @classmethod
    def includes(cls) -> list[str]:
        return [
            'CITATION.cff',
        ]


    @classmethod
    def excludes(cls) -> list[str]:
        return []


    @classmethod
    def analyse(cls, root: Path, files: list[Path]) -> dict:

        report = {
            'status': 'exists' if files else 'missing'
        }

        invalids = []

        if len(files) > 1:
            invalid.append("Multiple citation files found.")
            
        for file in files:
            with open(root / file, "r", encoding="utf-8") as stream:
                content = yaml.safe_load(stream)
                
            

        return report