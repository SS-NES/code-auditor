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
    def aggregate(cls, report: Report, results: dict):
        """Aggregates available analysis results.

        Args:
            report (Report): Analysis report.
            results (dict): Analyser results.
        """
        raise NotImplementedError
