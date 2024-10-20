"""Python packaging analyser module."""
from pathlib import Path
try: import tomllib
except ModuleNotFoundError: import pip._vendor.tomli as tomllib

from . import Analyser, AnalyserType, Report

import logging
logger = logging.getLogger(__name__)


class PackagingPython(Analyser):
    """Python packaging class.

    Core metadata specification is available at:
    https://packaging.python.org/en/latest/specifications/core-metadata/

    Version specifiers information is available at:
    https://packaging.python.org/en/latest/specifications/version-specifiers/
    """
    @staticmethod
    def get_type() -> AnalyserType:
        """Returns analyser type."""
        return AnalyserType.PACKAGING


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be included in the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return [
            '/pyproject.toml',
            '/setup.py',
            '/setup.cfg'
        ]


    @classmethod
    def analyse_pyproject(cls, path: Path) -> dict:
        """Analyses a pyproject.toml file.

        pyproject.toml specification is available at:
        https://packaging.python.org/en/latest/specifications/pyproject-toml/

        - Metadata paths are relative to pyproject.toml.
        - List of classifiers is available at https://pypi.org/classifiers/.
        - Description is a one-liner summary

        Args:
            path (Path): Path of the file.

        Returns:
            Analysis results.
        """
        def _set(data, key):
            val = data.get(key)

            if isinstance(val, str):
                metadata[key + '_file'] = str(path.parent / val)

            elif isinstance(val, dict):
                if 'file' in val:
                    metadata[key + '_file'] = str(path.parent / val['file'])
                elif 'text' in val:
                    metadata[key] = val['text']

        metadata = {}
        invalids = []

        with open(path, 'rb') as file:
            data = tomllib.load(file)

        if 'project' in data:
            project = data['project']

            for key in [
                'name',
                'description',
                'version',
                'keywords'
            ]:
                val = project.get(key)
                if val:
                    metadata[key] = val

            _set(project, 'readme')

            if isinstance(project.get("license"), str):
                invalids.append("Invalid license identifier.")
            else:
                _set(project, 'license')

            for key in ['authors', 'maintainers']:
                for i, item in enumerate(project.get(key, [])):
                    if isinstance(item, dict):
                        person = {}
                        if item.get('name'):
                            person['name'] = item['name']
                        if item.get('email'):
                            person['email'] = item['email']
                        if person:
                            if key not in metadata:
                                metadata[key] = []
                            metadata[key].append(person)
                            continue

                    invalids.append(f"Invalid {key}[{i+1}].")

            for item in project.get('classifiers', []):
                parts = [part.strip() for part in item.split('::')]
                if parts[0] == 'License':
                    metadata['license_name'] = parts[-1]

        return {
            'metadata': metadata,
            'invalids': invalids,
        }


    @classmethod
    def analyse_setup_config(cls, path: Path) -> dict:
        metadata = {}
        invalids = []

        with open(path, 'rb') as file:
            data = tomllib.load(file)

        if 'metadata' in data:
            meta = data['metadata']

            for key in [
                'name',
                'version',
                'description',
                'long_description',
                'keywords',
            ]:
                val = project.get(key)
                if val:
                    metadata[key] = val

        return {
            'metadata': metadata,
            'invalids': invalids,
        }


    @classmethod
    def analyse_file(cls, path: Path, report: Report) -> dict:
        """Analyses a file.

        Args:
            path (Path): Path of the file.
            report (Report): Analysis report.

        Returns:
            Dictionary of the analysis result of the file.
        """
        if path.name == 'pyproject.toml':
            return cls.analyse_pyproject(path)

        elif path.name == 'setup.py':
            pass

        elif path.name == 'setup.cfg':
            return cls.analyse_setup_config(path)
