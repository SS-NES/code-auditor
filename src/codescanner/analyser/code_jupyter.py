"""Jupyter notebooks analyser module."""
import json
from pathlib import Path

from .code import Code
from ..report import Report


class CodeJupyter(Code):
    """Jupyter notebooks analyser class."""

    LATEST_NBFORMAT = 4
    """Latest notebook format version"""


    @classmethod
    def get_name(cls) -> str:
        """Returns analyser name."""
        return "Jupyter Notebooks"


    @classmethod
    def get_languages(cls) -> list[str]:
        """Returns list of languages supported by the analyser."""
        return ['ipynb']


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be included in the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return [
            '*.ipynb',
        ]


    @classmethod
    def excludes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be excluded from the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return [
            '.ipynb_checkpoints/',
        ]


    @classmethod
    def analyse_content(cls, content: str, report: Report, path: Path=None) -> dict:
        """Analyses a Jupyter notebook content.

        Results:
            nbformat (int): Notebook format version.
            nbformat_minor (int): Notebook format minor version.
            num_cells (int): Number of cells.

        Args:
            content (str): Jupyter notebook content.
            report (Report): Analysis report.
            path (Path): Path of the Jupyter notebook file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        # Parese notebook content
        content = json.loads(content)

        # Add warning if invalid notebook file
        if 'nbformat' not in content:
            report.add_warning(cls, "Invalid Jupyter Notebook file.", path)
            return

        # Add warning if notebook format is not up to date
        if content['nbformat'] < cls.LATEST_NBFORMAT:
            report.add_warning(cls, f"Jupyter Notebook format is not up to date (v{content['nbformat']}).", path)

        results = {
            'nbformat': content['nbformat'],
            'nbformat_minor': content['nbformat_minor'],
        }

        cells = []
        if 'worksheets' in content:
            for worksheet in content['worksheets']:
                cells.extend(worksheet.get('cells', []))

        elif 'cells' in content:
            cells = content['cells']

        results['num_cells'] = len(cells)

        for cell in cells:
            pass

        return results