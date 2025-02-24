"""Utilities module."""
import importlib
import inspect
import pkgutil
import re
from pathlib import Path


REGEXP_SNAKE_CASE = re.compile(r'(?<!^)(?=[A-Z])')
"""Snake case conversion regular expression."""


def get_class_name(cls) -> str:
    """Returns snake-case class name."""
    return REGEXP_SNAKE_CASE.sub('_', cls.__qualname__).lower()


def get_subclasses(cls) -> dict:
    """Returns available subclasses of the parent class.

    Args:
        cls (object): Parent class.

    Returns:
        Dictionary of the available subclasses (name: class).
    """
    subclasses = {}

    for _, name, _ in pkgutil.iter_modules([Path(inspect.getfile(cls)).parent]):

        module = importlib.import_module(f'.{name}', f'{cls.__module__}')

        for name, obj in inspect.getmembers(module, inspect.isclass):

            if issubclass(obj, cls) and obj is not cls:
                subclasses[get_class_name(obj)] = obj

    return subclasses