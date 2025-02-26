"""Documentation aggregator module."""
from . import Aggregator
from ..processor import ProcessorType
from ..report import Report


class Documentation(Aggregator):
    """Documentation aggregator class."""

    @classmethod
    def get_type(cls) -> ProcessorType:
        """Returns analyser type of the aggregator."""
        return ProcessorType.DOCUMENTATION


    @classmethod
    def aggregate(cls, report: Report, results: dict):
        """Aggregates available analysis results.

        Args:
            report (Report): Analysis report.
            results (dict): Analyser results.
        """
        if not results:
            report.add_issue(cls, "No documentation.")

        else:
            report.add_notice(cls, "Documentation exists.")

        # Check if changelog exists
        if report.metadata.has('changelog_file'):
            report.add_notice(cls, "Changelog file exists.")

        else:
            report.add_issue(cls, "No changelog file.")

