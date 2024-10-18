"""Python packaging analyser module."""
from pathlib import Path

from . import Analyser, AnalyserType

import logging
logger = logging.getLogger(__name__)


class PackagingPython(Analyser):
    @staticmethod
    def get_type() -> AnalyserType:
        return AnalyserType.PACKAGING


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        return [
            '/pyproject.toml',
            '/setup.py',
            '/setup.cfg'
        ]


    @classmethod
    def analyse(cls, root: Path, files: list[Path]) -> dict:

        report = {
            'status': 'exists' if files else 'missing'
        }

        for path in files:
            logger.info(f"Found {path}.")
            if path.name == 'pyproject.toml':
                pass
            elif path.name == 'setup.py':
                pass
            elif path.name == 'setup.cfg':
                pass
                
            
        return report