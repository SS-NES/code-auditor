"""Version control aggregator module."""
from . import Aggregator
from ..analyser import AnalyserType


class VersionControl(Aggregator):
    @staticmethod
    def get_type() -> AnalyserType:
        """Returns analyser type of the aggregator."""
        return AnalyserType.VERSION_CONTROL


    @classmethod
    def aggregate(cls, reports: dict) -> dict:
        """Aggregates available analysis reports.

        Args:
            reports (dict): Analysis reports.

        Raises:
            NotImplementedError
        """
        raise NotImplementedError
