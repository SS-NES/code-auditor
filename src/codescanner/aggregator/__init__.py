"""Aggregator module."""
from abc import ABC, abstractmethod
import logging

from ..analyser import AnalyserType

logger = logging.getLogger(__name__)


class Aggregator(ABC):
    @classmethod
    @abstractmethod
    def get_type(cls) -> AnalyserType:
        raise NotImplementedError