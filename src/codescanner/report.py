"""Analysis report module."""
import re
import json
import yaml
import jinja2
import pypandoc
import functools
from pathlib import Path

from .utils import get_id, OutputType

import logging
logger = logging.getLogger(__name__)


@functools.cache
def get_issues() -> dict:
    """Returns issue descriptions.

    Issue descriptions are loaded from the `templates/issues.yaml` file located
    in the package directory.
    """
    path = Path(__file__).parent / 'templates/issues.yaml'

    logger.debug(f"Loading issues from `{path}`.")
    with open(path, 'r', encoding='utf-8') as file:
        items = yaml.safe_load(file)

    for item in items:
        if 'match' in item:
            item['match'] = re.compile(item['match'])

    return items


def find_issue(msg: str) -> dict:
    """Returns issue description matching the message.

    Args:
        msg (str): Issue message.

    Returns:
        Dictionary of the issue description.
    """
    for issue in get_issues():
        if 'match' in issue:
            if issue['math'].fullmatch(msg):
                return issue
        elif msg == issue['name']:
            return issue


class Report:
    """Analysis report class."""

    def __init__(self, path: Path):
        """Initializes analysis report object.

        Args:
            path (Path): Path of the code base.
        """
        self.path = path
        self.issues = []
        self.notices = []
        self.metadata = {}
        self.results = {}
        self.stats = {}


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
        self.metadata[key].append((val, analyser, src))


    def add_issue(self, analyser, msg: str, path=None):
        """Adds an issue message.

        Args:
            analyser (Analyser): Analyser class.
            msg (str): Issue message.
            path: Path of the source file (optional).
        """
        item = {'msg': msg, 'analyser': analyser}
        if path:
            item['path'] = path if isinstance(path, Path) else Path(path)

        self.issues.append(item)


    def add_notice(self, analyser, msg: str, src=None):
        """Adds a notice message.

        Args:
            analyser (Analyser): Analyser class.
            msg (str): Notice message.
            src: Metadata attribute source (optional).
        """
        self.notices.append((msg, analyser, src))


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

        issues = []
        for item in self.issues:
            issue = {
                'msg': item['msg'],
                'analyser': get_id(item['analyser']),
            }
            if 'path' in item:
                issue['path'] = item['path'].as_posix()
            issues.append(issue)

        notices = [item[0] for item in self.notices]

        return {
            'metadata': metadata,
            'issues': issues,
            'notices': notices,
            'stats': self.stats if self.stats else {},
        }


    def output_issue(self, item):
        out = f"### {item['msg']}\n"

        issue = find_issue(item['msg'])
        if issue and 'suggestion' in issue:
            out += issue['suggestion']

        return out


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
                autoescape=jinja2.select_autoescape(),
                trim_blocks=True
            )
            env.filters['issue'] = self.output_issue
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