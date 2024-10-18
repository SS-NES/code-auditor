"""Git analyser module."""
from pathlib import Path

from . import Analyser, AnalyserType


class Git(Analyser):
    @staticmethod
    def get_type() -> AnalyserType:
        return AnalyserType.VERSION_CONTROL


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        return [
            '.git/',
        ]


    @classmethod
    def excludes(cls, path: Path) -> list[str]:
        items = [
            '.git/'
        ]

        ignore_file = path / ".gitignore"
        if ignore_file.exists():
            with open(ignore_file, "r") as file:
                for line in file:
                    line = line.strip()
                    if not line.startswith("#") and line.endswith("/"):
                        items.append(line)

        return items


    @classmethod
    def analyse(cls, root: Path, files: list[Path]) -> dict:

        report = {
            'status': 'exists' if files else 'missing'
        }

        return report