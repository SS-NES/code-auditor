"""Packaging aggregator module."""
from . import Aggregator
from ..processor import ProcessorType
from ..report import Report


class Packaging(Aggregator):
    """Packaging aggregator class."""

    @classmethod
    def get_type(cls) -> ProcessorType:
        """Returns analyser type of the aggregator."""
        return ProcessorType.PACKAGING


    @classmethod
    def aggregate(cls, report: Report, results: dict):
        """Aggregates available analysis results.

        Args:
            report (Report): Analysis report.
            results (dict): Analyser results.
        """
        if not results:
            report.add_issue(cls, "No packaging.")

        else:
            report.add_notice(cls, "Packaging exists.")

