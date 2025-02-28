"""Jupyter notebooks analyser module."""
import json
from pathlib import Path

from . import Analyser
from .code import Code
from .code_markdown import CodeMarkdown
from ..processor import ProcessorType
from ..report import Report


CELL_TYPES = {
    'raw': "Raw",
    'code': "Code",
    'markdown': "Markdown",
    'html': "HTML",
    'heading': "Heading",
}


class JupyterNotebook(Analyser):
    """Jupyter notebooks analyser class."""

    LATEST_NBFORMAT = 4
    """Latest notebook format version"""


    @classmethod
    def get_type(cls) -> ProcessorType:
        """Returns analyser type."""
        return ProcessorType.CODE


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
        """Analyses Jupyter notebook.

        Results:
            nbformat (int): Notebook format version.
            nbformat_minor (int): Notebook format minor version.
            num_total_cells (int): Number of cells.

        Args:
            content (str): Jupyter notebook content.
            report (Report): Analysis report.
            path (Path): Path of the file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        # Parse notebook content
        notebook = json.loads(content)

        # Add warning if invalid notebook file
        if 'nbformat' not in notebook:
            report.add_warning(cls, "Invalid Jupyter Notebook file.", path)
            return

        # Add warning if notebook format is not up to date
        if notebook['nbformat'] < cls.LATEST_NBFORMAT:
            report.add_warning(cls, f"Jupyter Notebook format is not up to date (v{notebook['nbformat']}).", path)

        results = {
            'nbformat': notebook['nbformat'],
            'nbformat_minor': notebook['nbformat_minor'],
        }

        cells = []
        if 'worksheets' in notebook:
            for worksheet in notebook['worksheets']:
                cells.extend(worksheet.get('cells', []))

        elif 'cells' in notebook:
            cells = notebook['cells']

        results['size'] = len(content)
        results['num_total_cells'] = len(cells)
        results['num_cells'] = {}
        results['cells'] = {}

        index = 0
        for cell in cells:

            index += 1
            type = cell['cell_type']
            if type not in results['num_cells']:
                results['num_cells'][type] = 0

            results['num_cells'][type] += 1

            if type == 'markdown':
                analyser = CodeMarkdown
                result = analyser.analyse_code(content, report, path, [
                    'md041'
                ])

            elif type == 'code':
                lang = notebook['metadata']['language_info']['name'].lower()
                analyser = Code.get_analysers(lang)[0]
                if not analyser:
                    continue
                result = analyser.analyse_code(content, report, path)

            else:
                continue

            results['cells'][index] = {
                'analyser': analyser,
                'result': result
            }

        return results


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

        size = 0
        num_files = len(results)
        num_cells = {}
        num_total_cells = 0

        for path, result in results.items():
            size += result['size']
            num_total_cells += result['num_total_cells']
            for key, val in result['num_cells'].items():
                if key not in num_cells:
                    num_cells[key] = 0
                num_cells[key] += val

        out = report.output_heading("Jupyter Notebooks", 2)
        out += "{} {} found ({}).\n".format(
            num_files,
            'files' if num_files > 1 else 'file',
            report.output_size(size)
        )
        out += "There are {} cells. {} cells are code ({}), {} cells are documentation ({}).\n".format(
            report.output_number(num_total_cells),
            report.output_number(num_cells.get('code', 0)),
            report.output_ratio(num_cells.get('code', 0), num_total_cells),
            report.output_number(num_cells.get('markdown', 0)),
            report.output_ratio(num_cells.get('markdown', 0), num_total_cells),
        )

        out += "\n"

        for path, result in results.items():
            part = ''

            for index, cell in result['cells'].items():
                if not cell['analyser'] or not cell['result']:
                    continue

                out_result = cell['analyser'].output_result(report, cell['result'])
                if out_result:
                    part += out_result
                    part += "\n"
                    part += "(Cell {})\n\n".format(index)

            if part:
                out += report.output_heading(str(path.relative_to(report.path)), 3)
                out += part + "\n"

        out += "\n"

        return out
