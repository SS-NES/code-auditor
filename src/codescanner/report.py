"""Analysis report module."""
import functools
import jinja2
import json
import locale
import math
import pypandoc
import re
import yaml
from datetime import datetime
from enum import Enum
from pathlib import Path

from .metadata import Metadata


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

    def get_plural_name(self) -> str:
        return {
            1: "Information",
            2: "Suggestions",
            3: "Notices",
            4: "Warnings",
            5: "Issues",
        }[self.value]


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


def serialize(val, key: str=None):
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
        return {key: serialize(item) for key, item in val.items()}

    elif isinstance(val, list):
        return [serialize(item) for item in val]

    return val


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
        metadata (Metadata): Metadata.
        results (dict): Analyser results (analyser: result).
        stats (dict): Statistics.
    """
    def __init__(self, path: Path):
        """Initializes analysis report object.

        Args:
            path (Path): Path of the code base.
        """
        self.path = path
        self.messages = {type: [] for type in MessageType}
        self.metadata = Metadata()
        self.results = {}
        self.stats = {}


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
            if not self.metadata.has(key):
                pass

        for key in self.metadata.keys():
            if key not in metadata:
                self.add_issue(self, f"Missing metadata attribute {key}.")


    def as_dict(
        self,
        level: MessageType = MessageType.NOTICE,
        plain: bool = False
    ) -> dict:
        """Converts analysis report into a dictionary.

        Args:
            level (MessageType): Minimum message level (default = MessageType.NOTICE)
            plain (bool): Set True for a plain dictionary (default = False)

        Returns:
            Report dictionary.
        """
        def _serialize(item: dict, key: str=None, plain: bool=False) -> dict:
            val = serialize(item['val'], key)

            if plain:
                return val

            out = {
                'val': val,
                'analyser': item['analyser'].get_class_name(),
            }

            if item['path']:
                path = [
                    str(path.relative_to(self.path))
                    for path in (item['path'] if isinstance(item['path'], list) else [item['path']])
                ]
                out['path'] = path[0] if len(path) < 2 else path

            return out

        metadata = {}
        for key in self.metadata.keys():
            if plain:
                metadata[key] = serialize(self.metadata.get(key, plain=True), key)
            else:
                metadata[key] = [_serialize(item, key) for item in self.metadata.get(key)]

        out = {
            'metadata': metadata,
            'stats': serialize(self.stats),
        }

        for type in MessageType:
            if level.value <= type.value:
                out[type.name.lower()] = [
                    _serialize(item, plain=plain)
                    for item in self.messages[type]
                ]

        return out


    def output_heading(self, val: str, level: int=1) -> str:
        """Returns heading output.

        Args:
            val (str): Value.
            level (int): Heading level (default = 1)

        Returns:
            Heading output.
        """
        underlines = {1: '=', 2: '-', 3: '`', 4: "'", 5: '.'}
        return (
            val + "\n" +
            underlines.get(level, underlines[1]) * len(val) + "\n\n"
        )


    def output_number(self, val, format: str=None):
        """Returns number output.

        Args:
            val: Value.
            format (str): Number format (optional)

        Returns:
            Number output.
        """
        if not format:
            format = '%d' if isinstance(val, int) else '%f'

        return locale.format_string(format, val, grouping=True)


    def output_size(self, size: int) -> str:
        """Returns data size output.

        Args:
            size (int): Data size.

        Return:
            Data size output.
        """
        units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size, 1024)))
        return "{} {}".format(round(size / math.pow(1024, i), 2), units[i])


    def output_message(self, item: dict, plain: bool=False) -> str:
        """Generates message output.

        Args:
            item (dict): Message item.

        Returns:
            Message output.
        """
        out = "* " + item['val'] + "\n"

        if plain:
            return out

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
            out += self.output_heading("CodeScanner Analysis Report")

            out += "Code quality and conformity for software development best practices analysis report of {}.\n".format(
                self.metadata.get('name', plain=True, first=True, default="Unnamed Software")
            )
            out += "The software is located at ``{}``.\n".format(
                self.stats['path']
            )
            out += "\n"

            # Output messages
            for type in MessageType:

                if level.value > type.value:
                    continue

                if not self.messages[type] and type != MessageType.ISSUE:
                    continue

                out += self.output_heading(type.get_plural_name(), 2)

                if self.messages[type]:
                    for item in self.messages[type]:
                        out += self.output_message(item) + "\n"

                elif type == MessageType.ISSUE:
                    out += "No issues found.\n\n"

            # Output processor results
            for processor, results in self.results.items():
                if results:
                    out += processor.output(self, results)

            # Output metadata
            out += "Metadata\n"
            out += "--------\n\n"

            keys = self.metadata.keys()

            for key in keys:
                out += key + ": " + str(self.metadata.get(key, plain = True))
                out += "\n\n"

            if not keys:
                out += "No metadata found.\n"

            # Output footer
            out += "\n\n----\n\n"
            out += "| Created by `CodeScanner <https://github.com/SS-NES/codescanner>`_ v{} on {}.\n".format(
                self.stats['version'],
                serialize(self.stats['date'])
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
                    date = serialize(self.stats['date']).replace(':', '-')
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