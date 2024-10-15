"""Code aggregator module."""
from . import Aggregator
from ..analyser import AnalyserType


class Code(Aggregator):
    @staticmethod
    def get_type() -> AnalyserType:
        return AnalyserType.CODE


    @classmethod
    def analyse(cls, report: dict) -> dict:
        raise NotImplementedError
