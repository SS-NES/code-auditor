"""Python analyser module."""
import sys
import ast
import docstring_parser
from pathlib import Path

from . import Analyser, AnalyserType


def _analyse_node(node) -> dict:
    """Documentation."""
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

    docs = ast.get_docstring(node, clean=True)
    if not docs:
        item['docs'] = 'missing'

    else:
        item['docs'] = 'exists'

        docstring = docstring_parser.parse(docs)

        invalids = []

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
                item[f"docs.{key}"] = val

                if key == 'params':
                    if hasattr(node, "args") and len(val) != len(node.args.args):
                        invalids.append("Invalid number of arguments.")

        if invalids:
            item['docs.invalids'] = invalids

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

    if modules:
        report['modules'] = modules

    return report


class Python(Analyser):
    @staticmethod
    def get_type() -> AnalyserType:
        return AnalyserType.CODE


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        return [
            '*.py',
        ]


    @classmethod
    def excludes(cls, path: Path) -> list[str]:
        return [
            '__pycache__/',
        ]


    @classmethod
    def analyse_file(cls, path: Path) -> dict:
        with open(path, 'r') as file:
            node = ast.parse(file.read(), filename=path, type_comments=True)
            result = _analyse_node(node)

        return result
