"""Metadata aggregator module."""
from . import Aggregator
from ..analyser import AnalyserType
from ..report import Report


class Metadata(Aggregator):
    """Metadata aggregator class."""

    @classmethod
    def get_type(cls) -> AnalyserType:
        """Returns analyser type of the aggregator."""
        return AnalyserType.METADATA


    @classmethod
    def get_name(cls) -> str:
        """Returns aggregator name."""
        return "Metadata Aggregator"


    @classmethod
    def aggregate(cls, report: Report, results: dict):
        """Aggregates available analysis results.

        Args:
            report (Report): Analysis report.
            results (dict): Analyser results.
        """
        # For each metadata attribute
        for key in report.metadata.keys():

            # Get metadata attribute items
            items = report.metadata.get(key)

            # Skip if unique value
            if len(items) < 2:
                continue

            # Check if it is a value list
            if report.metadata.is_list(key):
                continue

            for item in items[1:]:
                if item['val'] == items[0]['val']:
                    continue

                report.add_issue(
                    cls,
                    f"Multiple values exists for {key}.",
                    [items[0]['path'], item['path']]
                )