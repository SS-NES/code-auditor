"""Aggregator module."""
from abc import ABC, abstractmethod

from ..analyser import AnalyserType

import logging
logger = logging.getLogger(__name__)


class Aggregator(ABC):
    """Aggregator abstract class."""

    @staticmethod
    @abstractmethod
    def get_type() -> AnalyserType:
        """Returns analyser type of the aggregator."""
        raise NotImplementedError


    @classmethod
    @abstractmethod
    def aggregate(cls, reports: dict) -> dict:
        """Aggregates available analysis reports.

        Args:
            reports (dict): Analysis reports.
        """
        raise NotImplementedError