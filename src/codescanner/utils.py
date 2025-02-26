"""Utilities module."""
import importlib
import inspect
import pkgutil
import re
from pathlib import Path


import logging
logger = logging.getLogger(__name__)


REGEXP_SNAKE_CASE = re.compile(r'(?<!^)(?=[A-Z])')
"""Snake case conversion regular expression."""


def get_class_name(cls) -> str:
    """Returns snake-case class name.

    Args:
        cls (object): Class.

    Returns:
        Snake-case class name.
    """
    return REGEXP_SNAKE_CASE.sub('_', cls.__qualname__).lower()


def get_subclasses(cls) -> list:
    """Returns available subclasses of the parent class.

    Subclasses with abstract methods are skipped.

    Args:
        cls (object): Parent class.

    Returns:
        List of the available subclasses.
    """
    subclasses = []

    for _, name, _ in pkgutil.iter_modules([Path(inspect.getfile(cls)).parent]):

        module = importlib.import_module(f'.{name}', f'{cls.__module__}')

        for name, obj in inspect.getmembers(module, inspect.isclass):

            if issubclass(obj, cls) and obj is not cls:
                if not obj.__abstractmethods__:
                    subclasses.append(obj)
                else:
                    logger.debug(f"{obj} has abstract methods, skipping.")

    if callable(getattr(cls, 'get_rank', None)):
        subclasses.sort(key = lambda item: item.get_rank())

    return subclasses