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


import logging
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Message type."""
    INFO = 1
    """Informational only, no action required."""
    SUGGESTION = 2
    """A recommended improvement for better code quality."""
    NOTICE = 3
    """Something noteworthy but not necessarily problematic."""
    WARNING = 4
    """A potential issue that should be addressed."""
    ISSUE = 5
    """A problem that needs to be fixed."""


class OutputType(Enum):
    """Output type."""
    PLAIN = 'plain'
    """Plain text"""
    HTML = 'html'
    """HTML"""
    JSON = 'json'
    """JSON"""
    YAML = 'yaml'
    """YAML"""
    MARKDOWN = 'markdown'
    """Markdown"""
    RST = 'rst'
    """reStructuredText"""
    RTF = 'rtf'
    """Rich text format"""
    DOCX = 'docx'
    """Office Open XML"""


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
        results (dict): Analyser results (analyser: result).
        stats (dict): Statistics.

    Class Attributes:
        counter (int): Counter.
        REGEXP_DOI: Regular expression for DOI validation.
        REGEXP_URL: Regular expression for URL validation.
    """
    REGEXP_DOI = re.compile(r"10\.\d{4,9}/[-._;()/:a-z\d]+", re.IGNORECASE)
    REGEXP_URL = re.compile(r"((http|ftp)(s)?):\/\/(www\.)?[a-z\d@:%._\+~#=-]{2,256}\.[a-z]{2,6}\b([-a-z\d@:%_\+.~#?&//=]*)", re.IGNORECASE)

    METADATA = [
        # Authors of the software.
        'authors',
        # Date the software has been released (YYYY-MM-DD).
        'date_released',
        # Description of the software.
        'description',
        # DOI of the software.
        'doi',
        # Keywords that describe the software.
        'keywords',
        # SPDX license identifier of the software.
        'license',
        # Name of the software license.
        'license_name',
        # File name of the software license.
        'license_file',
        # URL address of the software license.
        'license_url',
        # Long description of the software.
        'long_description',
        # Maintainers of the software.
        'maintainers',
        # Name of the software.
        'name',
        # List of dependency packages of the software (Python).
        'python_dependencies',
        # Readme of the software.
        'readme',
        # Readme file of the software.
        'readme_file',
        # URL of the source code repository of the software.
        'repository_code',
        # Version of the software.
        'version',
        # Version control system of the software.
        'version_control',
    ]

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


    def has_metadata(self, key: str) -> bool:
        """Checks is metadata attribute value exists.

        Args:
            key (str): Metadata attribute key.

        Returns:
            True if metadata attribute value exists, False otherwise.
        """
        return True if key in self.metadata else False


    def get_metadata(self, key: str):
        """Returns a metadata attribute value.

        Args:
            key (str): Metadata attribute key.

        Returns:
            First metadata attribute value if exists, None otherwise.
        """
        return self.metadata[key][0]['val'] if key in self.metadata else None


    def get_metadata_as_dict(self) -> dict:
        """Returns metadata as a dictionary.

        Returns:
            Metadata dictionary.
        """
        return {key: items[0]['val'] for key, items in self.metadata.items()}


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
                'path': Path(path) if isinstance(path, str) else path,
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

        if path:
            if not isinstance(path, list):
                path = [path]

            path = [item if isinstance(item, Path) else Path(item) for item in path]

        self.messages[type].append({'val': msg, 'analyser': analyser, 'path': path})


    def add_issue(self, analyser, msg: str, path: Path | list[Path]=None):
        """Adds an issue message.

        Args:
            analyser (Analyser): Analyser class.
            msg (str): Issue message.
            path (Path | list[Path]): Path of the source file(s) (optional).
        """
        self.add_message(MessageType.ISSUE, analyser, msg, path)


    def add_warning(self, analyser, msg: str, path: Path | list[Path]=None):
        """Adds a warning message.

        Args:
            analyser (Analyser): Analyser class.
            msg (str): Issue message.
            path (Path | list[Path]): Path of the source file(s) (optional).
        """
        self.add_message(MessageType.WARNING, analyser, msg, path)


    def add_notice(self, analyser, msg: str, path: Path | list[Path]=None):
        """Adds a notice message.

        Args:
            analyser (Analyser): Analyser class.
            msg (str): Notice message.
            path (Path | list[Path]): Path of the source file(s) (optional).
        """
        self.add_message(MessageType.NOTICE, analyser, msg, path)


    def add_suggestion(self, analyser, msg: str, path: Path | list[Path]=None):
        """Adds a suggestion message.

        Args:
            analyser (Analyser): Analyser class.
            msg (str): Notice message.
            path (Path | list[Path]): Path of the source file(s) (optional).
        """
        self.add_message(MessageType.SUGGESTION, analyser, msg, path)


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
                self.add_issue(self, f"Missing metadata attribute {key}.")


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
                'analyser': item['analyser'].get_name(),
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
        }

        for type in MessageType:
            if level.value <= type.value:
                out[type.name.lower()] = [
                    _serialize(item, plain=plain)
                    for item in self.messages[type]
                ]

        return out


    def output_message(self, item: dict, plain: bool=False) -> str:
        """Generates message output.

        Args:
            item (dict): Message item.

        Returns:
            Message output.
        """
        if plain:
            return "* " + item['val'] + "\n"

        out = "* " + item['val'] + "\n"

        issue = find_issue(item['val'])
        if issue and 'suggestion' in issue:
            out += "  " + "\n"
            out += "  " + issue['suggestion'] + "\n"

        if item['path']:
            out += (
                "  " +
                "(" +
                ", ".join(map(
                    lambda path: str(path.relative_to(self.path)),
                    item['path']
                )) +
                ")" +
                "\n"
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
            out = ''

            # Output header
            out += "CodeScanner Analysis Report\n"
            out += "===========================\n\n"

            out += "Code quality and conformity for software development best practices analysis report of {}.\n".format(
                self.get_metadata('name') if self.has_metadata('name') else "Unnamed Software"
            )
            out += "The software is located at ``{}``.\n".format(
                self.stats['path']
            )
            out += "\n"

            # Output issues
            out += "Issues\n"
            out += "------\n\n"

            if self.messages[MessageType.ISSUE]:
                for item in self.messages[MessageType.ISSUE]:
                    out += self.output_message(item) + "\n"

            else:
                out += "No issues found.\n"

            # Output analyser results
            for analyser, results in self.results.items():
                out += analyser.output(self, results)

            # Output metadata
            out += "Metadata\n"
            out += "--------\n\n"

            if self.metadata:
                for key, items in self.metadata.items():
                    out += key + ": " + str(self.output_metadata(items, key))
                    out += "\n\n"

            else:
                out += "No metadata found.\n"

            # Output footer
            out += "\n\n----\n\n"
            out += "| Created by `CodeScanner <https://github.com/SS-NES/codescanner>`_ v{} on {}.\n".format(
                self.stats['version'],
                self.serialize(self.stats['date'])
            )
            out += "| {} directories and {} files were analysed, {} directories were skipped.\n".format(
                self.stats['num_dirs'],
                self.stats['num_files'],
                self.stats['num_dirs_excluded']
            )
            out += "| Analysis finished in {} s.\n".format(
                round(self.stats['duration'], 2)
            )

            # Apply report template
            env = jinja2.Environment(
                loader=jinja2.PackageLoader('codescanner'),
                autoescape=jinja2.select_autoescape(),
                trim_blocks=True
            )
            template = env.get_template('report.rst')
            out = template.render(output = out)

            # Return if native format is requested
            if format == OutputType.RST:
                return out

            # Ensure pandoc is installed
            pypandoc.ensure_pandoc_installed()

            # Check if binary output is required
            if format in [OutputType.RTF, OutputType.DOCX]:
                # Create path if required
                if not path:
                    date = self.serialize(self.stats['date']).replace(':', '-')
                    path = f"report_{date}.{format.value}"

                # Save output file
                pypandoc.convert_text(
                    out,
                    format.value,
                    format='rst',
                    outputfile=path,
                    extra_args=['--standalone']
                )

                # Return output file path
                return path if isinstance(path, Path) else Path(path)

            else:
                # Return converted output
                return pypandoc.convert_text(out, format.value, format='rst')