"""License aggregator module."""
from . import Aggregator
from ..analyser import AnalyserType
from ..report import Report


class License(Aggregator):
    @classmethod
    def get_type(cls) -> AnalyserType:
        """Returns analyser type of the aggregator."""
        return AnalyserType.LICENSE


    @classmethod
    def aggregate(cls, report: Report, results: dict):
        """Aggregates available analysis results.

        Args:
            report (Report): Analysis report.
            results (dict): Analyser results.
        """
        raise NotImplementedError
