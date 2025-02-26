"""Code aggregator module."""
from . import Aggregator
from ..processor import ProcessorType
from ..report import Report


class Code(Aggregator):
    """Code aggregator class."""

    @classmethod
    def get_type(cls) -> ProcessorType:
        """Returns analyser type of the aggregator."""
        return ProcessorType.CODE


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

