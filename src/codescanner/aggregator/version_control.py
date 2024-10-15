"""Version control aggregator module."""
from . import Aggregator
from ..analyser import AnalyserType


class VersionControl(Aggregator):
    @staticmethod
    def get_type() -> AnalyserType:
        return AnalyserType.VERSION_CONTROL


    @classmethod
    def analyse(cls, report: dict) -> dict:
        raise NotImplementedError
