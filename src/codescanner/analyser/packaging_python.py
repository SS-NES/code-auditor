"""Python packaging analyser module."""
from pathlib import Path
try:
    import tomllib
except ModuleNotFoundError:
    import pip._vendor.tomli as tomllib

from . import Analyser, AnalyserType
from ..report import Report


class PackagingPython(Analyser):
    """Python packaging class.

    Core metadata specification is available at:
    https://packaging.python.org/en/latest/specifications/core-metadata/

    Version specifiers information is available at:
    https://packaging.python.org/en/latest/specifications/version-specifiers/
    """

    @classmethod
    def get_type(cls) -> AnalyserType:
        """Returns analyser type."""
        return AnalyserType.PACKAGING


    @classmethod
    def get_name(cls) -> str:
        """Returns analyser name."""
        return "Python Packaging"


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
    def analyse_pyproject(cls, path: Path, report: Report) -> dict:
        """Analyses a pyproject.toml file.

        pyproject.toml specification is available at:
        https://packaging.python.org/en/latest/specifications/pyproject-toml/

        - Metadata paths are relative to pyproject.toml.
        - List of classifiers is available at https://pypi.org/classifiers/.
        - Description is a one-liner summary

        Args:
            path (Path): Path of the pyproject.toml file.
            report (Report): Analysis report.

        Returns:
            Dictionary of the analysis results.
        """
        def _set(data, key):
            val = data.get(key)

            if isinstance(val, str):
                report.add_metadata(
                    cls,
                    key + '_file',
                    (path.parent / val).relative_to(report.path),
                    path
                )

            elif isinstance(val, dict):
                if 'file' in val:
                    report.add_metadata(
                        cls,
                        key + '_file',
                        (path.parent / val['file']).relative_to(report.path),
                        path
                    )
                elif 'text' in val:
                    report.add_metadata(cls, key, val['text'])

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
                    report.add_metadata(cls, key, val, path)

            _set(project, 'readme')

            if isinstance(project.get('license'), str):
                report.add_issue(cls, "Invalid license identifier.", path)
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
                        report.add_metadata(cls, key, person, path)
                        continue

                    report.add_issue(cls, f"Invalid {key}[{i+1}].", path)

            for item in project.get('classifiers', []):
                parts = [part.strip() for part in item.split('::')]
                if parts[0] == 'License':
                    report.add_metadata(cls, 'license_name', parts[-1], path)


    @classmethod
    def analyse_setup_config(cls, path: Path, report: Report) -> dict:
        """Analyses a setup.cfg file.

        setup.cfg specification is available at:
        https://setuptools.pypa.io/en/latest/userguide/declarative_config.html

        Args:
            path (Path): Path of the setup.cfg file.
            report (Report): Analysis report.

        Returns:
            Dictionary of the analysis results.
        """
        with open(path, 'rb') as file:
            data = tomllib.load(file)

        if 'metadata' in data:
            for key in [
                'name',
                'version',
                'description',
                'long_description',
                'keywords',
            ]:
                val = data['metadata'].get(key)
                report.add_metadata(cls, key, val, path)


    @classmethod
    def analyse_file(cls, path: Path, report: Report) -> dict:
        """Analyses a packaging file.

        Args:
            path (Path): Path of the packaging file.
            report (Report): Analysis report.

        Returns:
            Dictionary of the analysis results.
        """
        if path.name == 'pyproject.toml':
            return cls.analyse_pyproject(path, report)

        elif path.name == 'setup.py':
            pass

        elif path.name == 'setup.cfg':
            return cls.analyse_setup_config(path, report)
