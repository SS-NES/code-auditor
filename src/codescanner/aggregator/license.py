"""License aggregator module."""
from . import Aggregator
from ..analyser import AnalyserType
from ..report import Report


class License(Aggregator):
    """License aggregator class."""

    @classmethod
    def get_type(cls) -> AnalyserType:
        """Returns analyser type of the aggregator."""
        return AnalyserType.LICENSE


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
            report.add_metadata(cls, 'license_file', path.relative_to(report.path), path)
            report.add_metadata(cls, 'license', item['ids'][0], path)

