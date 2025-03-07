"""Repository aggregator module."""
from . import Aggregator
from ..processor import ProcessorType
from ..report import Report


class Repository(Aggregator):
    """Repository aggregator class."""

    @classmethod
    def get_type(cls) -> ProcessorType:
        """Returns analyser type of the aggregator."""
        return ProcessorType.REPOSITORY


    @classmethod
    def aggregate(cls, report: Report, results: dict):
        """Aggregates available analysis results.

        Args:
            report (Report): Analysis report.
            results (dict): Analyser results.
        """
        raise NotImplementedError
