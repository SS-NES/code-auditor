"""Community aggregator module."""
from . import Aggregator
from ..processor import ProcessorType
from ..report import Report


class Community(Aggregator):
    """Community aggregator class."""

    @classmethod
    def get_type(cls) -> ProcessorType:
        """Returns analyser type of the aggregator."""
        return ProcessorType.COMMUNITY


    @classmethod
    def aggregate(cls, report: Report, results: dict):
        """Aggregates available analysis results.

        Args:
            report (Report): Analysis report.
            results (dict): Analyser results.
        """
        if report.metadata.has('contributing_file'):
            report.add_notice(cls, "Contributing guidelines exists.")
        else:
            report.add_issue(cls, "No contributing guidelines.")


        if report.metadata.has('conduct_file'):
            report.add_notice(cls, "Code of conduct exists.")
        else:
            report.add_issue(cls, "No code of conduct.")

        if report.metadata.has('notice_file'):
            report.add_notice(cls, "Notice file exists.")
