"""Aggregator module."""
from abc import abstractmethod

from ..processor import Processor, ProcessorType
from ..report import Report


class Aggregator(Processor):
    """Aggregator abstract class."""

    @classmethod
    @abstractmethod
    def aggregate(cls, report: Report, results: dict) -> dict:
        """Returns aggregated analysis results of the analyser results.

        Args:
            report (Report): Analysis report.
            results (dict): Analyser results.

        Returns:
            Dictionary of the aggregation results.
        """
        raise NotImplementedError
