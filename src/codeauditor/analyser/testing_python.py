"""Python testing analyser module."""
from pathlib import Path

from . import Analyser
from .code_python import CodePython
from ..processor import ProcessorType
from ..report import Report


class TestingPython(Analyser):
    """Python testing analyser class."""

    @classmethod
    def get_type(cls) -> ProcessorType:
        """Returns analyser type."""
        return ProcessorType.TESTING


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be included in the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return [
            'tests/test_*.py',
            'tests/*_test.py',
        ]


    @classmethod
    def analyse_content(cls, content: str, report: Report, path: Path=None) -> dict:
        """Analyses content.

        Args:
            content (str): Content.
            report (Report): Analysis report.
            path (Path): Path of the content file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        result = CodePython.analyse_code(content, report, path)

        if "pytest" in result.get('modules', []):
            num_tests = 0
            for item in result.values():
                if (
                    isinstance(item, dict) and
                    item['type'] == 'function' and
                    item['name'].startswith('test_')
                ):
                    num_tests += 1

            return {
                'framework': 'pytest',
                'num_tests': num_tests,
            }
