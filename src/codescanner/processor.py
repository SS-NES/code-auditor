"""Processor module."""
import importlib
import inspect
import pkgutil
import re
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

from .report import Report


import logging
logger = logging.getLogger(__name__)


REGEXP_SNAKE_CASE = re.compile(r'(?<!^)(?=[A-Z])')
"""Snake case conversion regular expression."""


class ProcessorType(Enum):
    """Processor type."""
    CITATION = "Citation"
    """Citation."""
    CODE = "Code"
    """Source code."""
    COMMUNITY = "Community"
    """Community."""
    DEPENDENCY = "Dependency"
    """Dependency management."""
    DOCUMENTATION = "Documentation"
    """Software documentation."""
    LICENSE = "License"
    """Software licensing."""
    METADATA = "Metadata"
    """Metadata."""
    PACKAGING = "Packaging"
    """Software packaging."""
    REPOSITORY = "Repository"
    """Code repository."""
    VERSION_CONTROL = "Version Control"
    """Version control system."""


class Processor(ABC):
    """Processor abstract class."""

    @classmethod
    @abstractmethod
    def get_type(cls) -> ProcessorType:
        """Returns type of the processor."""
        raise NotImplementedError


    @classmethod
    def get_rank(cls) -> int:
        """Returns processor rank."""
        return 1


    @classmethod
    def get_class_name(cls) -> str:
        """Returns snake-case class name."""
        return REGEXP_SNAKE_CASE.sub('_', cls.__qualname__).lower()


    @classmethod
    def get_subclasses(cls) -> list:
        """Returns list of available subclasses of the parent class.

        Subclasses with abstract methods are skipped.
        """
        subclasses = []

        for _, name, _ in pkgutil.iter_modules([Path(inspect.getfile(cls)).parent]):

            module = importlib.import_module(f'.{name}', f'{cls.__module__}')

            for name, obj in inspect.getmembers(module, inspect.isclass):

                if issubclass(obj, cls) and obj is not cls and obj not in subclasses:
                    if not obj.__abstractmethods__:
                        subclasses.append(obj)
                    else:
                        logger.debug(f"{obj} has abstract methods, skipping.")

        if callable(getattr(cls, 'get_rank', None)):
            subclasses.sort(key = lambda item: item.get_rank())

        return subclasses


    @classmethod
    def output(cls, report: Report, results: dict) -> str:
        """Generates output from the analysis report and results.

        Args:
            report (Report): Analysis report.
            results (dict): Analysis results.

        Returns:
            Analysis output.
        """
        return ''
