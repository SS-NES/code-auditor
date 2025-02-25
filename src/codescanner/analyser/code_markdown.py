"""Markdown code analyser module."""
from pathlib import Path
from pymarkdown.api import PyMarkdownApi, PyMarkdownApiException

from .code import Code
from ..report import Report


class CodeMarkdown(Code):
    """Markdown code analyser class."""

    @classmethod
    def get_name(cls) -> str:
        """Returns analyser name."""
        return "Markdown Code"


    @classmethod
    def get_languages(cls) -> list[str]:
        """Returns list of languages supported by the analyser."""
        return ['markdown']


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be included in the analysis.

        For a potential list of extensions see:
        https://superuser.com/questions/249436/

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return [
            '*.markdown',
            '*.md',
            '*.mdown',
            '*.mdtext',
            '*.mdtxt',
            '*.mdwn',
            '*.mkd',
            '*.text',
            '*.txt',
        ]


    @classmethod
    def analyse_content(cls, content: str, report: Report, path: Path=None) -> dict:
        """Analyses Markdown content.

        Args:
            content (str): Markdown content.
            report (Report): Analysis report.
            path (Path): Path of the Markdown file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        try:
            result = PyMarkdownApi().scan_string(content)

        except PyMarkdownApiException as err:
            report.add_warning(cls, err, path)
            return

        return result
