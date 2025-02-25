"""Python dependency analyser module."""
from pathlib import Path
from pip_requirements_parser import RequirementsFile

from . import Analyser, AnalyserType
from ..report import Report


class DependencyPython(Analyser):
    """Python dependency analyser class."""

    @classmethod
    def get_type(cls) -> AnalyserType:
        """Returns analyser type."""
        return AnalyserType.DEPENDENCY


    @classmethod
    def get_name(cls) -> str:
        """Returns analyser name."""
        return "Python Dependency"


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be included in the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return [
            '/requirements.txt',
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
        # FIXME: RequirementFile.from_string fails because it doesnt load pathlib
        reqfile = RequirementsFile.from_file(path)

        for req in reqfile.requirements:

            if not req.specifier:
                report.add_issue(cls, f"{req.name} dependency has no version specifier.", path)

            elif not req.is_pinned:
                report.add_issue(cls, f"{req.name} dependency version is not pinned.", path)

        results = reqfile.to_dict()

        return results