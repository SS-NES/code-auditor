"""License aggregator module."""
from . import Aggregator
from ..processor import ProcessorType
from ..report import Report


class License(Aggregator):
    """License aggregator class."""

    @classmethod
    def get_type(cls) -> ProcessorType:
        """Returns analyser type of the aggregator."""
        return ProcessorType.LICENSE


    @classmethod
    def aggregate(cls, report: Report, results: dict):
        """Aggregates available analysis results.

        Args:
            report (Report): Analysis report.
            results (dict): Analyser results.
        """
        if not results:
            report.add_issue(cls, "No license file.")
            return

        if len(results) > 1:
            report.add_issue(cls, "Multiple license files found.", results.keys())

        else:
            report.add_notice(cls, "License file exists.")

        for path, item in results.items():
            report.metadata.add(cls, 'license_file', path.relative_to(report.path), path)
            report.metadata.add(cls, 'license', item['ids'][0], path)

