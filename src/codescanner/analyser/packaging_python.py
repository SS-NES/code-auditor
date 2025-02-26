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
    def analyse_pyproject(cls, content: str, report: Report, path: Path=None) -> dict:
        """Analyses a pyproject.toml content.

        pyproject.toml specification is available at:
        https://packaging.python.org/en/latest/specifications/pyproject-toml/

        - Metadata paths are relative to pyproject.toml.
        - List of classifiers is available at https://pypi.org/classifiers/.
        - Description is a one-liner summary.

        Args:
            content (str): Content.
            report (Report): Analysis report.
            path (Path): Path of the content file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        def _set(data, key):
            val = data.get(key)

            if isinstance(val, str):
                file_path = path.parent / val
                report.metadata.add(
                    cls,
                    key + '_file',
                    file_path.relative_to(report.path),
                    path
                )
                if not file_path.exists():
                    report.add_issue(cls, f"{key}_file does not exist.", path)

            elif isinstance(val, dict):
                if 'file' in val:
                    file_path = (path.parent / val['file'])
                    report.metadata.add(
                        cls,
                        key + '_file',
                        file_path.relative_to(report.path),
                        path
                    )
                    if not file_path.exists():
                        report.add_issue(cls, f"{key}_file does not exist.", path)

                if 'text' in val:
                    report.metadata.add(cls, key, val['text'], path)

        try:
            data = tomllib.loads(content)

        except tomllib.TOMLDecodeError:
            report.add_issue(cls, "Invalid pyproject.toml file.", path)
            return

        if 'project' in data:
            project = data['project']

            for key in [
                'name',
                'description',
                'version',
                'keywords',
            ]:
                report.metadata.add(cls, key, project.get(key), path)

            _set(project, 'readme')

            if isinstance(project.get('license'), str):
                report.add_issue(cls, "Invalid license identifier.", path)
            else:
                _set(project, 'license')

            for key in ['authors', 'maintainers']:
                persons = []

                for i, item in enumerate(project.get(key, [])):
                    if isinstance(item, dict):
                        person = {}
                        if item.get('name'):
                            person['name'] = item['name']
                        if item.get('email'):
                            person['email'] = item['email']
                        persons.append(person)
                        continue

                    report.add_issue(cls, f"Invalid {key}[{i+1}].", path)

                if persons:
                    report.metadata.add(cls, key, persons, path)

            for item in project.get('classifiers', []):
                parts = [part.strip() for part in item.split('::')]
                if parts[0] == 'License':
                    report.metadata.add(cls, 'license_name', parts[-1], path)


    @classmethod
    def analyse_setup_config(cls, content: str, report: Report, path: Path=None) -> dict:
        """Analyses a setup.cfg content.

        setup.cfg specification is available at:
        https://setuptools.pypa.io/en/latest/userguide/declarative_config.html

        Args:
            content (str): Content.
            report (Report): Analysis report.
            path (Path): Path of the content file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        try:
            data = tomllib.loads(content)

        except tomllib.TOMLDecodeError:
            report.add_issue(cls, "Invalid setup.cfg file.", path)
            return

        if 'metadata' in data:
            for key in [
                'name',
                'version',
                'description',
                'long_description',
                'keywords',
            ]:
                val = data['metadata'].get(key)
                report.metadata.add(cls, key, val, path)


    @classmethod
    def analyse_content(cls, content: str, report: Report, path: Path=None) -> dict:
        """Analyses content.

        Args:
            content (str): Content.
            report (Report): Analysis report.
            path (Path): Path of the content file (optional).

        Returns:
            Dictionary of the analysis results.
        """
        if path.name == 'pyproject.toml':
            return cls.analyse_pyproject(content, report, path)

        elif path.name == 'setup.py':
            report.add_issue(cls, "Using setup.py for packaging is not suggested.", path)

        elif path.name == 'setup.cfg':
            return cls.analyse_setup_config(content, report, path)
