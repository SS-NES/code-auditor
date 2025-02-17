"""Analysis report module."""
import re
import json
import yaml
import jinja2
import pypandoc
import functools
from enum import Enum
from pathlib import Path
from datetime import datetime

from .utils import get_id, OutputType, MessageType

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


def is_list(items: list[dict]) -> bool:
    """Checks if items contain a list.

    Args:
        items (list[dict]): Items

    Returns:
        True if items contain a list, False otherwise.
    """
    ids = set()

    for item in items:
        if item['id'] in ids:
            return True

        ids.add(item['id'])

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
        messages (dict): List of messages.
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
        self.messages = {type: [] for type in MessageType}
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
        # For each metadata attribute
        for key, items in self.metadata.items():

            # Skip if unique value
            if len(items) < 2:
                continue

            # Check if it is a value list
            if is_list(items):
                continue

            for item in items[1:]:
                if item['val'] == items[0]['val']:
                    continue

                self.add_issue(
                    self,
                    f"Multiple values exists for {key}.",
                    [items[0]['path'], item['path']]
                )


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


    def add_message(self, type: MessageType, analyser, msg: str, path: Path | list[Path]=None):
        """Adds a message.

        Args:
            type (MessageType): Message type.
            analyser (Analyser): Analyser class.
            msg (str): Issue message.
            path (Path | list[Path]): Path of the source file(s) (optional).

        Raises:
            ValueError("Invalid message type.")
        """
        if not isinstance(type, MessageType):
            raise ValueError("Invalid message type.")

        if path and not isinstance(path, list):
            path = [path]

        self.messages[type].append({'val': msg, 'analyser': analyser, 'path': path})


    def add_issue(self, analyser, msg: str, path: Path | list[Path]=None):
        """Adds an issue message.

        Args:
            analyser (Analyser): Analyser class.
            msg (str): Issue message.
            path (Path | list[Path]): Path of the source file(s) (optional).
        """
        self.add_message(MessageType.ISSUE, analyser, msg, path)


    def add_notice(self, analyser, msg: str, path: Path | list[Path]=None):
        """Adds a notice message.

        Args:
            analyser (Analyser): Analyser class.
            msg (str): Notice message.
            path (Path | list[Path]): Path of the source file(s) (optional).
        """
        self.add_message(MessageType.NOTICE, analyser, msg, path)


    def add_info(self, analyser, msg: str, path: Path | list[Path]=None):
        """Adds an info message.

        Args:
            analyser (Analyser): Analyser class.
            msg (str): Info message.
            path (Path | list[Path]): Path of the source file(s) (optional).
        """
        self.add_message(MessageType.INFO, analyser, msg, path)


    def compare(self, metadata: dict):
        """Compares reference metadata with the report metadata.

        Adds messages for the identified issues.

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


    def as_dict(
        self,
        level: MessageType = MessageType.NOTICE,
        plain: bool = False
    ) -> dict:
        """Converts analysis report into a dictionary.

        Args:
            plain (bool): Set True for a plain dictionary (default = False)

        Returns:
            Report dictionary.
        """
        def _serialize(item: dict, key: str=None, plain: bool=False) -> dict:
            if plain:
                return self.serialize(item['val'], key)

            if isinstance(item['path'], list):
                path = [str(path.relative_to(self.path)) for path in item['path']]
            elif item['path']:
                path = str(item['path'].relative_to(self.path))
            else:
                path = None

            return {
                'val': self.serialize(item['val'], key),
                'analyser': get_id(item['analyser']),
                'path': path,
            }

        metadata = {}
        for key, items in self.metadata.items():
            metadata[key] = [_serialize(item, key) for item in items]
            if plain:
                metadata[key] = self.output_metadata(metadata[key], key)

        out = {
            'metadata': metadata,
            'stats': self.serialize(self.stats),
            'issues': [_serialize(item, plain=plain) for item in self.messages[MessageType.ISSUE]],
        }

        if level.value <= MessageType.NOTICE.value:
            out['notices'] = [_serialize(item, plain=plain) for item in self.messages[MessageType.NOTICE]]

        if level.value <= MessageType.INFO.value:
            out['infos'] = [_serialize(item, plain=plain) for item in self.messages[MessageType.INFO]]

        return out


    def output_message(self, item: dict) -> str:
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
            out += (
                "(" +
                ", ".join(map(
                    lambda path: str(path.relative_to(self.path)),
                    item['path'] if isinstance(item['path'], list) else [item['path']]
                )) +
                ")"
            )

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

        for item in items:

            if item['val'] not in out:
                out.append(item['val'])

        if is_list(items) or (not one and len(out) > 1):
            return out

        return out.pop()


    def output(
        self,
        format: OutputType = OutputType.PLAIN,
        level: MessageType = MessageType.NOTICE,
        plain: bool = False,
        path = None
    ) -> str | Path:
        """Generates analysis report output.

        Args:
            format (OutputType): Output format (default = OutputType.PLAIN)
            level (MessageType): Minimum message level (default = MessageType.NOTICE)
            plain (bool): Set True to get plain output for JSON and YAML (default = False)
            path (str): Path of the output file (optional)

        Returns:
            Analysis report output.
        """
        if format == OutputType.JSON:
            return json.dumps(
                self.as_dict(level = level, plain = plain),
                indent = 4
            )

        elif format == OutputType.YAML:
            return yaml.dump(self.as_dict(level = level, plain = plain))

        else:
            env = jinja2.Environment(
                loader=jinja2.PackageLoader('codescanner'),
                autoescape=jinja2.select_autoescape(),
                trim_blocks=True
            )
            env.filters.update({
                'metadata': self.output_metadata,
                'issue': self.output_issue,
                'message': self.output_message,
                'serialize': self.serialize,
            })

            out = {
                'metadata': self.metadata,
                'stats': self.stats,
                'issues': self.messages[MessageType.ISSUE],
            }

            if level.value <= MessageType.NOTICE.value:
                out['notices'] = self.messages[MessageType.NOTICE]

            if level.value <= MessageType.INFO.value:
                out['infos'] = self.messages[MessageType.INFO]

            template = env.get_template('report.md')
            out = template.render(**out)

            if format == OutputType.MARKDOWN:
                return out

            pypandoc.ensure_pandoc_installed()

            if format in [OutputType.RTF, OutputType.DOCX]:
                if not path:
                    date = self.serialize(self.stats['date']).replace(':', '-')
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