"""Git version control analyser module."""
import git
from pathlib import Path

from . import Analyser, AnalyserType
from ..report import Report


class Git(Analyser):
    """Git version control analyser class."""

    @classmethod
    def get_type(cls) -> AnalyserType:
        """Returns analyser type."""
        return AnalyserType.VERSION_CONTROL


    @classmethod
    def includes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be included in the analysis.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        return [
            '.git/',
        ]


    @classmethod
    def excludes(cls, path: Path) -> list[str]:
        """Returns file and directory patterns to be excluded from the analysis.

        Reads .gitignore file to retrieve the list of directories to be
        excluded.

        Args:
            path (Path): Path of the code base.

        Returns:
            List of file and directory patterns.
        """
        items = [
            '.git/'
        ]

        ignore_file = path / '.gitignore'
        if ignore_file.exists():
            with open(ignore_file, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line.startswith('#') and line.endswith('/'):
                        items.append(line)

        return items


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
        pass


    @classmethod
    def analyse_file(cls, path: Path, report: Report) -> dict:
        """Analyses a git file.

        Args:
            path (Path): Path of the git file.
            report (Report): Analyse report.

        Returns:
            Dictionary of the analysis results.
        """
        try:
            repo = git.Repo(path)

        except git.exc.InvalidGitRepositoryError as err:
            report.add_warning(cls, "Invalid git repository.", path)
            return

        # Set version control metadata
        report.metadata.add(cls, 'version_control', 'git', path)

        # Set code repository URL address metadata if remote repository exists
        for remote in repo.remotes:

            if remote.name == 'origin':
                report.metadata.add(cls, 'repository_code', remote.url, path)
