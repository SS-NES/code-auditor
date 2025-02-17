"""License aggregator module."""
from pathlib import Path

from . import Aggregator
from ..analyser import AnalyserType
from ..report import Report


class License(Aggregator):
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

        elif len(results) > 1:
            report.add_issue(cls, "Multiple license files found.")

        else:
            report.add_notice(cls, "License file exists.")

            if 'license_file' in report.metadata:
                license_file = report.metadata['license_file'][0]['val']
                file = list(results.keys())[0]

                if license_file.name != file:
                    report.add_issue(cls, f"License files do not match: {license_file}, {file}")

            if 'license' in report.metadata:
                license = report.metadata['license'][0]['val']
                found = False
                for file, item in results.items():
                    if "ids" in item and license.lower() in item['ids']:
                        found = True
                if not found:
                    report.add_issue(cls, f"License identifier {license} does not match the license file.")