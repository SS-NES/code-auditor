"""Analysis report module."""
import re
import json
import yaml
import jinja2
import pypandoc
import functools
from pathlib import Path
from datetime import datetime

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
            if issue['match'].fullmatch(msg):
                return issue
        elif msg == issue['name']:
            return issue


def is_empty(val) -> bool:
    """Checks if value is empty.

    Args:
        val: Value

    Returns:
        True if value is empty, False otherwise.
    """
    if val is None:
        return True

    if isinstance(val, str) and val.strip() == '':
        return True

    if isinstance(val, dict) or isinstance(val, list):
        for item in val:
            if not is_empty(item):
                return False
        return True

    return False


class Report:
    """Analysis report class.

    Statistics object:
        path (Path): Analysis path.
        date (datetime.datetime): Analysis start date.
        end_date (datimetime.datetime): Analysis end date.
        duration (float): Analysis duration in seconds.
        version (str): Package version.
        num_dirs (int): Number of directories analysed.
        num_dirs_excluded (int): Number of directories excluded from analysis.
        num_files (int): Number of files analysed.

    Attributes:
        path (Path): Path of the code base.
        issues (list): List of issues.
        notices (list): List of notices.
        metadata (dict): Metadata.
        results (dict): Analyser results (id: result).
        stats (dict): Statistics.

    Class Attributes:
        counter (int): Counter.
        REGEXP_DOI: Regular expression for DOI validation.
        REGEXP_URL: Regular expression for URL validation.
    """
    REGEXP_DOI = re.compile(r"10\.\d{4,9}/[-._;()/:a-z\d]+", re.IGNORECASE)
    REGEXP_URL = re.compile(r"((http|ftp)(s)?):\/\/(www\.)?[a-z\d@:%._\+~#=-]{2,256}\.[a-z]{2,6}\b([-a-z\d@:%_\+.~#?&//=]*)", re.IGNORECASE)


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
        self.uid = 0


    def validate_metadata(self, key: str, val):
        """Validates metadata value.

        Args:
            key (str): Metadata attribute key.
            val: Metadata attribute value.

        Raises:
            ValueError: If metadata value is invalid.
        """
        # Digital Object Identifier (DOI)
        if key == 'doi':
            if not re.fullmatch(Report.REGEXP_DOI, val):
                raise ValueError("Invalid DOI.")

        elif key in ['repository_code']:
            if not re.fullmatch(Report.REGEXP_URL, val):
                raise ValueError("Invalid URL address.")


    def analyse_metadata(self):
        for key, items in self.metadata.items():
            # TODO: Analyse metadata attribute
            pass


    def add_metadata(self, analyser, key: str, val, path: Path=None):
        """Adds a metadata attribute.

        Args:
            analyser (Analyser): Analyser class.
            key (str): Metadata attribute key.
            val: Metadata attribute value(s).
            path (Path): Path of the source file (optional).
        """
        # Return if empty value
        if is_empty(val):
            return

        # Initialize metadata list if required
        if key not in self.metadata:
            self.metadata[key] = []

        # Increase id counter
        self.uid += 1

        # For each value
        for _val in val if isinstance(val, list) else [val]:

            # Skip if empty value
            if is_empty(val):
                continue

            # Validate value
            try:
                self.validate_metadata(key, _val)

            except Exception as err:
                self.add_issue(analyser, key, str(err), path)

            # Add value to metadata list
            self.metadata[key].append({
                'val': _val,
                'analyser': analyser,
                'path': path,
                'id': self.uid,
            })


    def add_issue(self, analyser, msg: str, path: Path=None):
        """Adds an issue message.

        Args:
            analyser (Analyser): Analyser class.
            msg (str): Issue message.
            path (Path): Path of the source file (optional).
        """
        self.issues.append({'val': msg, 'analyser': analyser, 'path': path})


    def add_notice(self, analyser, msg: str, path: Path=None):
        """Adds a notice message.

        Args:
            analyser (Analyser): Analyser class.
            msg (str): Notice message.
            path (Path): Path of the source file (optional).
        """
        self.notices.append({'val': msg, 'analyser': analyser, 'path': path})


    def compare(self, metadata: dict):
        """Compares reference metadata with the report metadata.

        Adds issues and notices for the identified issues.

        Args:
            metadata (dict): Reference metadata.
        """
        for key, val in metadata:
            if key not in self.metadata:
                pass

        for key, items in self.metadata:
            if key not in metadata:
                self.add_issue(f"Missing metadata attribute {key}.")


    def serialize(self, val, key: str=None) -> str:
        """Serializes value.

        Args:
            val: Value
            key (str): Value key (optional)

        Returns:
            Serialized value.
        """
        if isinstance(val, Path):
            return str(val)

        if isinstance(val, datetime):
            return val.isoformat(timespec='seconds')

        elif isinstance(val, dict):
            return {key: self.serialize(item, key) for key, item in val.items()}

        elif isinstance(val, list):
            return [self.serialize(item) for item in val]

        return val


    def as_dict(self, plain: bool=False) -> dict:
        """Converts analysis report into a dictionary.

        Args:
            plain (bool): Set True for a plain dictionary (default = False)

        Returns:
            Report dictionary.
        """
        def _serialize(item: dict, key: str=None, plain: bool=False) -> dict:
            if plain:
                return self.serialize(item['val'], key)

            return {
                'val': self.serialize(item['val'], key),
                'analyser': get_id(item['analyser']),
                'path': str(item['path'].relative_to(self.path)) if item['path'] else None,
            }

        metadata = {}
        for key, items in self.metadata.items():
            metadata[key] = [_serialize(item, key) for item in items]
            if plain:
                metadata[key] = self.output_metadata(metadata[key], key)

        return {
            'metadata': metadata,
            'issues': [_serialize(item, plain=plain) for item in self.issues],
            'notices': [_serialize(item, plain=plain) for item in self.notices],
            'stats': self.serialize(self.stats),
        }


    def output_notice(self, item: dict) -> str:
        """Generates notice output.

        Args:
            item (dict): Notice item.

        Returns:
            Notice output.
        """
        return f"- {item['val']}"


    def output_issue(self, item: dict) -> str:
        """Generates issue output.

        Args:
            item (dict): Issue item.

        Returns:
            Issue output.
        """
        out = f"### {item['val']}\n"

        issue = find_issue(item['val'])
        if issue and 'suggestion' in issue:
            out += issue['suggestion'] + "\n"

        if item['path']:
            out += f"(`{item['path']}`)\n"

        return out


    def output_metadata(self, items: list, key: str=None, one: bool=False, default: str=None) -> str:
        """Generates metadata output.

        Args:
            items (list): Metadata attribute items.
            key (str): Metadata attribute key (optional).
            one (bool): Set True to return a single attribute value (default = False)
            default (str): Default value if no attribute items (optional)

        Returns:
            Metadata output.
        """
        if not items:
            return default

        out = []
        ids = set()
        is_list = False

        for item in items:
            if not is_list and 'id' in item:
                if item['id'] in ids:
                    is_list = True
                else:
                    ids.add(item['id'])

            if item['val'] not in out:
                out.append(item['val'])

        if is_list or (not one and len(out) > 1):
            return out

        return out.pop()


    def output(self, format: OutputType=OutputType.PLAIN, plain: bool=False, path=None) -> str | Path:
        """Generates analysis report output.

        Args:
            format (OutputType): Output format (default = OutputType.PLAIN)
            plain (bool): Set True to get plain output for JSON and YAML (default = False)
            path (str): Path of the output file (optional)

        Returns:
            Analysis report output.
        """
        if format == OutputType.JSON:
            return json.dumps(self.as_dict(plain), indent=4)

        elif format == OutputType.YAML:
            return yaml.dump(self.as_dict(plain))

        else:
            report = self.as_dict()

            env = jinja2.Environment(
                loader=jinja2.PackageLoader('codescanner'),
                autoescape=jinja2.select_autoescape(),
                trim_blocks=True
            )
            env.filters.update({
                'notice': self.output_notice,
                'issue': self.output_issue,
                'metadata': self.output_metadata,
            })
            template = env.get_template('report.md')
            out = template.render(**report)

            if format == OutputType.MARKDOWN:
                return out

            pypandoc.ensure_pandoc_installed()

            if format in [OutputType.RTF, OutputType.DOCX]:
                if not path:
                    date = report['stats']['date'].replace(':', '-')
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