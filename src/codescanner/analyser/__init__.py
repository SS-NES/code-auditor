"""Analyser module."""
from abc import abstractmethod
from pathlib import Path

from ..processor import Processor, ProcessorType
from ..report import Report


import logging
logger = logging.getLogger(__name__)


class Analyser(Processor):
    """Analyse abstract class."""

    @classmethod
    @abstractmethod
    def includes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be included in the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        raise NotImplementedError


    @classmethod
    def excludes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be excluded from the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return []


    @classmethod
    @abstractmethod
    def analyse_content(cls, content: str, report: Report, path: Path=None) -> dict:
        """Analyses content.

        Args:
            content (str): Content.
            report (Report): Analysis report.
            path (Path): Path of the content file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        raise NotImplementedError


    @classmethod
    def analyse_file(cls, path: Path, report: Report) -> dict:
        """Analyses a file.

        Args:
            path (Path): Path of the file.
            report (Report): Analysis report.

        Returns:
            Dictionary of the analysis results.
        """
        if path.is_file():
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()

        else:
            content = None

        return cls.analyse_content(content, report, path)


    @classmethod
    def analyse_results(cls, results: dict, report: Report):
        """Analyses the analysis results of the files.

        Args:
            results (dict): Analysis results of the files.
            report (Report): Analysis report.
        """
        pass


    @classmethod
    def analyse(cls, root: Path, files: list[Path], report: Report) -> dict:
        """Performs the analysis of the files.

        Args:
            root (Path): Path of the code base.
            files (list[Path]): Paths of the files relative to the root path.
            report (Report): Analysis report.

        Returns:
            Dictionary of the analysis results of the files {path: result, ...}.
        """
        results = {}

        for file in files:
            logger.debug(f"Analysing `{file}`.")
            path = root / file
            try:
                results[path] = cls.analyse_file(path, report)

            except NotImplementedError:
                logger.debug(f"{cls} file analyser is not implemented.")
                continue

        cls.analyse_results(results, report)

        return results
