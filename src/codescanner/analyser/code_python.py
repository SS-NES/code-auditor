"""Python code analyser module."""
import ast
import docstring_parser
import sys
from pathlib import Path

from .code import Code
from ..report import Report


def _analyse_node(node) -> dict:
    """Analyses a code node.

    Analysis report:
        type (str): Node type (`module`, `class`, `function`)
        docs (dict): Documentation information.
        modules (list): List of modules.

    Args:
        node: Code node.

    Returns:
        Anaysis report.
    """
    item = {}

    if isinstance(node, ast.Module):
        item['type'] = 'module'

    elif isinstance(node, ast.ClassDef):
        item['type'] = 'class'

    elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
        item['type'] = 'function'

    else:
        return {}

    name = node.name if hasattr(node, 'name') else ''

    item['docs'] = {}

    docs = ast.get_docstring(node, clean=True)
    if docs:
        docstring = docstring_parser.parse(docs)

        issues = []

        for key in [
            'style',
            'short_description',
            'long_description',
            'params',
            'returns',
            'examples',
        ]:
            val = getattr(docstring, key)
            if val:
                item['docs'][key] = val

                if key == 'params':
                    if hasattr(node, 'args') and len(val) != len(node.args.args):
                        issues.append("Invalid number of arguments.")

        if issues:
            item['docs']['issues'] = issues

    report = {name: item}

    modules = set()

    for child in ast.iter_child_nodes(node):

        if isinstance(child, ast.Import):
            modules.update([item.name.split('.')[0] for item in child.names])

        if isinstance(child, ast.ImportFrom) and child.module and not child.level:
            modules.add(child.module.split('.')[0])

        else:
            result = _analyse_node(child)

            for key, val in result.items():

                if not val:
                    continue

                if key == 'modules':
                    modules.update(val)

                else:
                    report[name + '.' + key] = val

    modules = modules.difference(sys.stdlib_module_names)

    report['modules'] = modules

    return report


class CodePython(Code):
    """Python code analyser class."""

    @classmethod
    def get_languages(cls) -> list[str]:
        """Returns list of languages supported by the analyser."""
        return ['python']


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be included in the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return [
            '*.py',
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
            '__pycache__/',
        ]


    @classmethod
    def analyse_content(cls, content: str, report: Report, path: Path=None) -> dict:
        """Analyses a Python code content.

        Args:
            content (str): Python code content.
            report (Report): Analysis report.
            path (Path): Path of the Python file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        node = ast.parse(content, filename=path, type_comments=True)

        result = _analyse_node(node)

        return result


    @classmethod
    def analyse_results(cls, results: dict, report: Report):
        """Analyses the analysis results of the files.

        Args:
            results (dict): Analysis results of the files.
            report (Report): Analysis report.
        """
        modules = set()

        for path, result in results.items():
            modules.update(result['modules'])

        report.metadata.add(cls, 'python_dependencies', sorted(list(modules)))