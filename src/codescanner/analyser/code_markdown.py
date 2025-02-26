"""Markdown code analyser module."""
from pathlib import Path
from pymarkdown.api import PyMarkdownApi, PyMarkdownApiException

from .code import Code
from ..report import Report


import logging
logging.getLogger('pymarkdown').setLevel(logging.CRITICAL)


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

        except Exception as err:
            report.add_warning(cls, str(err), path)
            return

        return result


    @classmethod
    def output(cls, report: Report, results: dict) -> str:
        """Generates output from the analysis report and results.

        Args:
            report (Report): Analysis report.
            results (dict): Analysis results.

        Returns:
            Analysis output.
        """
        out = ''

        for path, result in results.items():

            if not result:
                continue

            part = ''

            for item in result.scan_failures:
                part += "* {}{} (Line {}).\n".format(
                    item.rule_description,
                    (" " + item.extra_error_information)
                    if item.extra_error_information
                    else
                    '',
                    item.line_number
                )

            for item in result.pragma_errors:
                part += "* {} (Line {}".format(
                    item.pragma_error,
                    item.line_number
                )

            if part:
                out += report.output_heading(str(path.relative_to(report.path)), 3)
                out += part + "\n"

        if out:
            out = report.output_heading("Markdown Files", 2) + out + "\n"

        return out
