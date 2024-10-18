"""
codescanner
"""
import pkgutil
import importlib
import inspect
import functools
import fnmatch
import re
from pathlib import Path
from dataclasses import dataclass

from .analyser import Analyser, AnalyserType
from .aggregator import Aggregator

import logging
logger = logging.getLogger(__name__)


"""Snake case conversion regular expression."""
REGEXP_SNAKE_CASE = re.compile(r"(?<!^)(?=[A-Z])")


@dataclass(init=False)
class Rule:
    val: str
    is_dir: bool
    is_pattern: bool
    is_nested: bool
    analysers: list[str]


    @staticmethod
    def _is_pattern(val: str) -> bool:
        """Checks if rule value is a pattern."""
        return ('*' in val) or ('?' in val) or ('[' in val)


    @staticmethod
    def _is_nested(val: str) -> bool:
        return ('/' in val)


    def __init__(self, val: str, analyser: str = None):
        self.is_dir = val[-1] == '/'
        if self.is_dir:
            val = val[:-1]
        self.is_nested = val[0] == '/'
        if self.is_nested:
            val = val[1:]
        else:
            self.is_nested = Rule._is_nested(val)
        self.is_pattern = Rule._is_pattern(val)
        self.val = val
        self.analysers = [analyser] if analyser else []


    def match(self, val: str) -> bool:
        return fnmatch.fnmatch(val, self.val)


def _snake_case(val: str) -> str:
    return REGEXP_SNAKE_CASE.sub('_', val).lower()


def _get_subclasses(parent) -> dict:
    """Returns available subclasses of the parent class.

    Args:
        parent (ob): Parent class.

    Returns:
        Dictionary of the available subclasses (name: class).
    """
    classes = {}

    for _, name, _ in pkgutil.iter_modules([Path(inspect.getfile(parent)).parent]):

        module = importlib.import_module(f".{name}", f"{parent.__module__}")

        for name, obj in inspect.getmembers(module, inspect.isclass):

            if issubclass(obj, parent) and obj is not parent:
                classes[_snake_case(name)] = obj

    return classes


@functools.cache
def get_analysers() -> dict:
    """Returns available analysers.

    Returns:
        Dictionary of the available analysers (name: class).

    Examples:
        >>> codescanner.get_analysers()
        >>> {'license': <class 'codescanner.analyser.license.License'>, ...}
    """
    return _get_subclasses(Analyser)


@functools.cache
def get_aggregators() -> dict:
    """Returns available aggregators.

    Returns:
        Dictionary of the available aggregators (name: class).

    Examples:
        >>> codescanner.get_aggregators()
        >>> {'code': <class 'codescanner.aggregator.code.Code'>, ...}
    """
    return _get_subclasses(Aggregator)


def _get_includes(path: Path, skip: list[str], skip_type: list[str]) -> dict:
    items = {}

    for name, analyser in get_analysers().items():

        if name in skip:
            continue

        if analyser.get_type().value in skip_type:
            continue

        for val in analyser.includes(path):

            if val not in items:
                items[val] = Rule(val)

            items[val].analysers.append(name)

    return items


def _get_excludes(path: Path) -> dict:
    items = {}

    for name, analyser in get_analysers().items():

        for val in analyser.excludes(path):

            rule = Rule(val, analyser)

            if not rule.is_dir:
                raise ValueError("Invalid exclusion rule.", val)

            items[val] = rule

    return items


def analyse(
    path: str,
    skip: list[str] = [],
    skip_type: list[str] = [],
) -> dict:
    """Analyses a code base.

    Args:
        path (str): Path of the code base.

    Returns:
        Dictionary of the analysis results.
    """
    path = Path(path)
    if not path.exists() or not path.is_dir():
        raise ValueError("Invalid path.")

    _skip = [_snake_case(item) for item in skip]
    _skip_type = [_snake_case(item) for item in skip_type]

    logger.info(f"Scanning '{path}'.")

    includes = _get_includes(path, _skip, _skip_type)
    excludes = _get_excludes(path)

    stats = {
        'num_dirs': 0,
        'num_dirs_excluded': 0,
        'num_files': 0,
    }

    groups = {}

    for root, dirs, files in path.walk(top_down=True, follow_symlinks=True):

        stats['num_dirs'] += 1

        excluded = []
        for dir in dirs:

            relpath = (root / dir).relative_to(path)

            for _, rule in includes.items():

                if not rule.is_dir:
                    continue

                if rule.match(relpath if rule.is_nested else dir):

                    for analyser in rule.analysers:

                        if analyser not in groups:
                            groups[analyser] = []

                        groups[analyser].append(relpath)

            for _, rule in excludes.items():

                if rule.match(relpath if rule.is_nested else dir):
                    stats['num_dirs_excluded'] += 1
                    excluded.append(dir)
                    logger.debug(f"Directory '{relpath}' excluded.")
                    break

        for dir in excluded:
            dirs.remove(dir)

        for file in files:

            relpath = (root / file).relative_to(path)

            for _, rule in includes.items():

                if rule.is_dir:
                    continue

                if rule.match(relpath if rule.is_nested else file):
                    stats['num_files'] += 1

                    for analyser in rule.analysers:

                        if analyser not in groups:
                            groups[analyser] = []

                        groups[analyser].append(relpath)

    report = {type: {} for type in AnalyserType}

    for name, analyser in get_analysers().items():

        if name in _skip:
            continue

        if analyser.get_type().value in _skip_type:
            continue

        type = analyser.get_type()
        files = groups.get(name, [])

        try:
            logger.info(f"Running {name} analyser.")
            report[type][name] = analyser.analyse(path, files)

        except NotImplementedError:
            logger.info(f"{name} analyser is not implemented.")
            pass

    for name, aggregator in get_aggregators().items():

        if name in _skip:
            continue

        type = aggregator.get_type()

        try:
            logger.info(f"Running {name} aggregator.")
            report[type] = aggregator.aggregate(report[type])

        except NotImplementedError:
            logger.info(f"{name} aggregator is not implemented.")
            pass

    return report


if __name__ == '__main__':
    raise NotImplementedError