"""
codescanner
"""
import pkgutil
import importlib
import inspect
import functools
import os
from pathlib import Path

from .rule import Rule
from .metadata import Metadata
from .analyser import Analyser
from .aggregator import Aggregator
from .utils import get_id, OutputType

import logging
logger = logging.getLogger(__name__)


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
                classes[get_id(obj)] = obj

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


def _get_includes(path: Path, analysers: dict = None) -> dict:
    items = {}

    if not analysers:
        analysers = get_analysers()

    for name, analyser in analysers.items():

        for val in analyser.includes(path):

            if val not in items:
                items[val] = Rule(val)

            items[val].analysers.append(name)

    return items


def _get_excludes(path: Path, analysers: dict = None) -> dict:
    items = {}

    if not analysers:
        analysers = get_analysers()

    for name, analyser in analysers.items():

        for val in analyser.excludes(path):

            rule = Rule(val, name)

            if not rule.is_dir:
                raise ValueError("Invalid exclusion rule.", val)

            items[val] = rule

    return items


def _filter(items: dict, skip: list[str] = [], skip_type: list[str] = []) -> dict:
    _items = {}
    for name, item in items.items():

        if name in skip:
            continue

        if item.get_type().name.lower() in skip_type:
            continue

        _items[name] = item

    return _items


def analyse(
    path: str | Path,
    skip: list[str] = [],
    skip_type: list[str] = [],
) -> dict:
    """Analyses a code base.

    Args:
        path (str): Path of the code base.
        skip (list[str]): List of analysers to skip (optional)
        skip_type (list[str]): List of analyser types to skip (optional)

    Returns:
        Dictionary of the analysis results.

    Raises:
        ValueError("Invalid path."): If path is invalid.
    """
    # Check if path is valid
    if not isinstance(path, Path):
        path = Path(path)

    if not path.exists() or not path.is_dir():
        raise ValueError("Invalid path.")

    # Find actual path if required
    while True:
        items = os.listdir(path)
        if len(items) != 1 or not os.path.isdir(path / items[0]):
            break
        path = path / items[0]
        logger.debug(f"Proceeding to `{path}`")

    # Get analysers and aggregators
    analysers = _filter(get_analysers(), skip, skip_type)
    aggregators = _filter(get_aggregators(), skip, skip_type)

    # Get inclusion and exclusion rules
    includes = _get_includes(path, analysers)
    excludes = _get_excludes(path)

    # Initialize statistics
    stats = {
        'num_dirs': 0,
        'num_dirs_excluded': 0,
        'num_files': 0,
    }

    _files = {}

    logger.debug(f"Scanning `{path}`.")
    for root, dirs, files in path.walk(top_down=True, follow_symlinks=True):

        stats['num_dirs'] += 1

        excluded = []
        for dir in dirs:

            relpath = (root / dir).relative_to(path)

            for _, rule in includes.items():

                if not rule.is_dir:
                    continue

                if rule.match(relpath if rule.is_nested else dir):

                    for id in rule.analysers:

                        if id not in _files:
                            _files[id] = []

                        _files[id].append(relpath)

            for _, rule in excludes.items():

                if rule.match(relpath if rule.is_nested else dir):
                    stats['num_dirs_excluded'] += 1
                    excluded.append(dir)
                    logger.debug(f"Directory `{relpath}` excluded.")
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

                    for id in rule.analysers:

                        if id not in _files:
                            _files[id] = []

                        _files[id].append(relpath)

    results = {}
    reports = {}

    # For each analyser
    for id, analyser in analysers.items():

        # Skip if no files are available for the analyser
        if id not in _files:
            continue

        # Try to run the analyser
        logger.debug(f"Running {id} analyser.")
        try:
            results[id] = analyser.analyse(path, _files[id])

        # Skip if not implemented
        except NotImplementedError:
            logger.debug(f"{id} analyser is not implemented.")
            continue

        type = analyser.get_type()
        if type not in reports:
            reports[type] = {}

        reports[type][id] = results[id]

    # For each aggregator
    for id, aggregator in aggregators.items():

        # Get aggregator type
        type = aggregator.get_type()

        # Try to run the aggregator
        logger.debug(f"Running {id} aggregator.")
        try:
            results[id] = aggregator.aggregate(reports.get(type, {}))

        # Skip if not implemented
        except NotImplementedError:
            logger.debug(f"{id} aggregator is not implemented.")
            continue

    return results


def output(results, format: OutputType=OutputType.TEXT) -> str:
    """Generates analysis results output.

    Args:
        results: Analysis results.
        format (OutputType): Output format (default = OutputType.TEXT)

    Returns:
        Analysis results output.
    """
    return results