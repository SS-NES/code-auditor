"""Documentation aggregator module."""
from . import Aggregator
from ..analyser import AnalyserType


class Documentation(Aggregator):
    @classmethod
    def get_type(cls) -> AnalyserType:
        """Returns analyser type of the aggregator."""
        return AnalyserType.DOCUMENTATION


    @classmethod
    def aggregate(cls, reports: dict) -> dict:
        """Aggregates available analyser reports.

        Args:
            reports (dict): Analyser reports.
        """
        raise NotImplementedError
