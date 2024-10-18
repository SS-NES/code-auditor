"""Jupyter analyser module."""
from pathlib import Path

from . import Analyser, AnalyserType


class Jupyter(Analyser):
    @staticmethod
    def get_type() -> AnalyserType:
        return AnalyserType.CODE


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        return [
            '*.ipynb',
        ]


    @classmethod
    def excludes(cls, path: Path) -> list[str]:
        return [
            '.ipynb_checkpoints/',
        ]


    @classmethod
    def analyse_file(cls, path: Path) -> dict:
        raise NotImplementedError