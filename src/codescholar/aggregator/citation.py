"""Citation aggregator module."""
from . import Aggregator
from ..processor import ProcessorType
from ..report import Report


class Citation(Aggregator):
    """Citation aggregator class."""

    @classmethod
    def get_type(cls) -> ProcessorType:
        """Returns analyser type of the aggregator."""
        return ProcessorType.CITATION


    @classmethod
    def aggregate(cls, report: Report, results: dict):
        """Aggregates available analysis results.

        Args:
            report (Report): Analysis report.
            results (dict): Analyser results.
        """
        if not results:
            report.add_issue(cls, "No citation file.")

        else:
            report.add_notice(cls, "Citation file exists.")
