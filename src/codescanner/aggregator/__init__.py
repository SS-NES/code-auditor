"""Aggregator module."""
from abc import ABC, abstractmethod

from ..analyser import AnalyserType


class Aggregator(ABC):
    """Aggregator abstract class."""

    @classmethod
    @abstractmethod
    def get_type(cls) -> AnalyserType:
        """Returns analyser type of the aggregator."""
        raise NotImplementedError


    @classmethod
    @abstractmethod
    def aggregate(cls, reports: dict) -> dict:
        """Aggregates available analyser reports.

        Args:
            reports (dict): Analyser reports.
        """
        raise NotImplementedError