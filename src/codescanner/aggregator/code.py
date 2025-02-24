"""Code aggregator module."""
from . import Aggregator
from ..analyser import AnalyserType
from ..report import Report


class Code(Aggregator):
    """Code aggregator class."""

    @classmethod
    def get_type(cls) -> AnalyserType:
        """Returns analyser type of the aggregator."""
        return AnalyserType.CODE


    @classmethod
    def get_name(cls) -> str:
        """Returns aggregator name."""
        return "Code Aggregator"


    @classmethod
    def aggregate(cls, report: Report, results: dict):
        """Aggregates available analysis results.

        Args:
            report (Report): Analysis report.
            results (dict): Analyser results.
        """
        if not results:
            report.add_issue(cls, "No software code.")

        else:
            report.add_notice(cls, "Software code exists.")

