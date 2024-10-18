"""Analyser module."""
from abc import ABC, abstractmethod
import logging
from enum import Enum
from pathlib import Path


logger = logging.getLogger(__name__)


class AnalyserType(Enum):
    CODE = 1
    VERSION_CONTROL = 2
    DOCUMENTATION = 3
    LICENSE = 4
    CITATION = 5
    REPOSITORY = 6
    PACKAGING = 7
    CONTINUOUS_INTEGRATION = 8


class Analyser(ABC):
    @staticmethod
    @abstractmethod
    def get_type() -> AnalyserType:
        raise NotImplementedError


    @classmethod
    @abstractmethod
    def includes(cls, path: Path) -> list[str]:
        raise NotImplementedError

    @classmethod
    def excludes(cls, path: Path) -> list[str]:
        return []


    @classmethod
    @abstractmethod
    def analyse_file(cls, path: Path) -> dict:
        raise NotImplementedError


    @classmethod
    def analyse_files(cls, root: Path, files: list[Path], skip_empty: bool=False) -> dict:
        report = {}

        for path in files:
            logger.debug(f"Analysing {path}.")

            result = cls.analyse_file(root / path)

            if not skip_empty or result:
                report[path.as_posix()] = result

        return report


    @classmethod
    def analyse(cls, root: Path, files: list[Path]) -> dict:
        report = {
            'files': cls.analyse_files(root, files),
        }

        return report


    @classmethod
    @abstractmethod
    def as_markdown(cls, report: dict) -> str:
        raise NotImplementedError