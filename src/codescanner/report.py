"""Analysis report module."""
from pathlib import Path
import json
import yaml
import jinja2
import pypandoc

from .utils import get_id, OutputType


class Report:
    """Analysis report class."""

    def __init__(self):
        """Initializes analysis report object."""
        self.issues = []
        self.notices = []
        self.metadata = {}
        self.stats = {}


    def _get_source(self, analyser, src=None):
        if isinstance(src, Path):
            src = src.as_posix()

        return get_id(analyser) + ((':' + src) if src else '')


    def add_metadata(self, analyser, key: str, val, src=None):
        """Adds a metadata attribute.

        Args:
            analyser (Analyser): Analyser class.
            key (str): Metadata attribute key.
            val: Metadata attribute value.
            src: Metadata attribute source (optional).
        """
        if key not in self.metadata:
            self.metadata[key] = []
        self.metadata[key].append((val, self._get_source(analyser, src)))


    def add_issue(self, analyser, msg: str, src=None):
        """Adds an issue message.

        Args:
            analyser (Analyser): Analyser class.
            msg (str): Issue message.
            src: Metadata attribute source (optional).
        """
        self.issues.append((msg, self._get_source(analyser, src)))


    def add_notice(self, analyser, msg: str, src=None):
        """Adds a notice message.

        Args:
            analyser (Analyser): Analyser class.
            msg (str): Notice message.
            src: Metadata attribute source (optional).
        """
        self.notices.append((msg, self._get_source(analyser, src)))


    def as_dict(self) -> dict:
        """Converts analysis report into a dictionary."""
        metadata = {}
        for key, items in self.metadata.items():
            if len(items) > 1:
                metadata[key] = []
                for item in items:
                    metadata[key].append(item[0])
            else:
                metadata[key] = items[0][0]

        issues = [item[0] for item in self.issues]

        notices = [item[0] for item in self.notices]

        return {
            'metadata': metadata,
            'issues': issues,
            'notices': notices,
            'stats': self.stats if self.stats else {},
        }


    def output(self, format: OutputType=OutputType.PLAIN, path=None) -> str:
        """Generates analysis report output.

        Args:
            format (OutputType): Output format (default = OutputType.PLAIN)

        Returns:
            Analysis report output.

        Raises:
            ValueError("Invalid output format.")
            ValueError("Output file is required.")
        """
        report = self.as_dict()

        if format == OutputType.JSON:
            return json.dumps(report, indent=4)

        elif format == OutputType.YAML:
            return yaml.dump(report, encoding='utf-8')

        else:
            env = jinja2.Environment(
                loader=jinja2.PackageLoader('codescanner'),
                autoescape=jinja2.select_autoescape()
            )
            template = env.get_template('report.md')
            out = template.render(**report)

            if format == OutputType.MARKDOWN:
                return out

            pypandoc.ensure_pandoc_installed()

            if format in [OutputType.RTF, OutputType.DOCX]:
                if not path:
                    date = report['stats']['date'].isoformat(timespec='seconds').replace(':', '-')
                    path = f"report_{date}.{format.value}"

                pypandoc.convert_text(
                    out,
                    format.value,
                    format='md',
                    outputfile=path,
                    extra_args=['--standalone']
                )

                return path if isinstance(path, Path) else Path(path)

            else:
                return pypandoc.convert_text(out, format.value, format='md')