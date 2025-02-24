"""Aggregator module."""
from abc import ABC, abstractmethod

from ..analyser import AnalyserType
from ..report import Report


class Aggregator(ABC):
    """Aggregator abstract class."""

    @classmethod
    @abstractmethod
    def get_type(cls) -> AnalyserType:
        """Returns analyser type of the aggregator."""
        raise NotImplementedError


    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """Returns aggregator name."""
        raise NotImplementedError


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
