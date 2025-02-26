"""Version control aggregator module."""
from . import Aggregator
from ..processor import ProcessorType
from ..report import Report


class VersionControl(Aggregator):
    """Version control aggregator class."""

    @classmethod
    def get_type(cls) -> ProcessorType:
        """Returns analyser type of the aggregator."""
        return ProcessorType.VERSION_CONTROL


    @classmethod
    def aggregate(cls, report: Report, results: dict):
        """Aggregates available analysis results.

        Args:
            report (Report): Analysis report.
            results (dict): Analyser results.
        """
        if not results:
            report.add_issue(cls, "No version control.")

        else:
            report.add_notice(cls, "Version control exists.")
