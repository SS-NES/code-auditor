"""Git analyser module."""
from pathlib import Path

from . import Analyser, AnalyserType


class Git(Analyser):
    @staticmethod
    def get_type() -> AnalyserType:
        return AnalyserType.VERSION_CONTROL


    @classmethod
    def includes(cls) -> list[str]:
        return [
            '.git/',
        ]


    @classmethod
    def excludes(cls) -> list[str]:
        return [
            '.git/'
        ]


    @classmethod
    def analyse(cls, root: Path, files: list[Path]) -> dict:

        report = {
            'status': 'exists' if files else 'missing'
        }

        return report