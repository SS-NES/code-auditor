import codescanner
from .analyser import AnalyserType
from .utils import OutputType, MessageType

import zipfile
import tarfile
import urllib.request
import git
import tempfile
import json
import yaml

import click

import logging
logger = logging.getLogger(__name__)


PATH_TYPES = [
    'zip',
    'tar', 'tgz', 'tar.gz',
    'git',
]


@click.command(
    context_settings = {
        'show_default': True,
    },
    help = "Scans the code base, where PATH is the path or URL address of the code base."
)
@click.argument(
    'path',
)
# Analysis options
@click.option(
    '--skip-analyser',
    type = click.Choice(
        codescanner.get_analysers().keys(),
        case_sensitive = False
    ),
    multiple = True,
    help = "List of analysers to skip."
)
@click.option(
    '--skip-aggregator',
    type = click.Choice(
        codescanner.get_aggregators().keys(),
        case_sensitive=False
    ),
    multiple = True,
    help = "List of aggregators to skip."
)
@click.option(
    '--skip-type',
    type = click.Choice(
        [item.name.lower() for item in AnalyserType],
        case_sensitive = False
    ),
    multiple = True,
    help = "List of analysers types to skip."
)
@click.option(
    '-r',
    '--reference',
    type = click.File('r', encoding='utf-8'),
    help = "Path of the reference metadata for comparison (e.g. SMP)."
)
# Remote repository options
@click.option(
    '-b',
    '--branch',
    type = click.STRING,
    help = "Branch or tag of the remote code repository."
)
@click.option(
    '-t',
    '--path-type',
    type = click.Choice(PATH_TYPES, case_sensitive = False),
    help = "Type of the file located at the path."
)
# Output options
@click.option(
    '-m',
    '--metadata',
    type = click.File('w', encoding='utf-8', lazy=True),
    help = "Path to store the metadata extracted from the code base."
)
@click.option(
    '-o',
    '--output',
    type = click.Path(),
    help = "Path to store the analysis output."
)
@click.option(
    '-f',
    '--format',
    type = click.Choice(
        [item.value for item in OutputType],
        case_sensitive = False
    ),
    default = OutputType.RST.value,
    help = "Output format."
)
@click.option(
    '-p',
    '--plain',
    type = click.BOOL,
    is_flag = True,
    default = False,
    help = "Enable plain output."
)
@click.option(
    '-l',
    '--message-level',
    'level',
    type = click.IntRange(
        min = MessageType.INFO.value,
        max = MessageType.ISSUE.value,
        clamp = True
    ),
    default = MessageType.NOTICE.value,
    help = "Message level.",
)
# Development options
@click.option(
    '-d',
    '--debug',
    type = click.BOOL,
    is_flag = True,
    default = False,
    help = "Enable debug mode."
)
@click.version_option(
    None,
    '-v',
    '--version'
)
@click.help_option(
    '-h',
    '--help'
)
def main(
    path,
    skip_analyser,
    skip_aggregator,
    skip_type,
    reference,
    branch,
    path_type,
    metadata,
    output,
    format,
    plain,
    level,
    debug,
):
    """Runs the command line interface (CLI).

    Args:
        path (str): Path of the code base.
        skip_analyser (list[str]): List of analysers to skip (optional).
        skip_aggregator (list[str]): List of aggregators to skip (optional).
        skip_type (list[str]): List of analyser types to skip (optional).
        reference (str): Path of the reference metadata for comparison (e.g. SMP) (optional).
        branch (str): Branch or tag of the remote repository (optional).
        path_type (str): Path type (optional).
        metadata (str): Path to store the metadata extracted from the code base (optional).
        output (str): Path to store the analysis output (optional).
        format (str): Output format (default = 'text').
        debug (bool): Debug flag (default = False).
    """
    logger.debug(f"Analysing `{path}`.")

    # Set logging level if debug flag is set
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logger.debug("Debugging enabled.")

    # Set path type if required
    if not path_type:
        for val in PATH_TYPES:
            if path.endswith('.' + val):
                path_type = val
                break

    if not path_type and not path.startswith('http'):
        try:
            if zipfile.is_zipfile(path):
                path_type = 'zip'

            elif tarfile.is_tarfile(path):
                path_type = 'tar'
        except:
            pass

    # Create temporary directory
    tempdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)

    try:
        is_local = False

        # Check if remote file
        if path.startswith('http') and path_type and path_type not in ('git'):
            # Retrieve remote file
            logger.debug(f"Retrieving `{path}`.")
            temppath, _ = urllib.request.urlretrieve(path)
            logger.debug(f"File stored as `{temppath}`.")
        else:
            temppath = None

        # Check if ZIP archive
        if path_type == 'zip':
            # Extract archive to the temporary directory
            logger.debug(f"Extracting {path_type} archive `{path}`.")
            with zipfile.ZipFile(temppath if temppath else path, 'r') as file:
                file.extractall(tempdir.name)

        # Check if TAR archive
        elif path_type in ('tar', 'tgz', 'tar.gz'):
            # Extract archive to the temporary directory
            logger.debug(f"Extracting {path_type} archive `{path}`.")
            with tarfile.open(temppath if temppath else path, 'r') as file:
                file.extractall(tempdir.name)

        # Check if git repository
        elif path_type == 'git' or path.startswith('http'):
            # Clone repository to the temporary directory
            logger.debug(f"Cloning `{path}`.")
            git.Repo.clone_from(path, tempdir.name, branch=branch)

        else:
            is_local = True

        # Generate analysis report
        report = codescanner.analyse(
            path if is_local else tempdir.name,
            skip_analyser=skip_analyser,
            skip_aggregator=skip_aggregator,
            skip_type=skip_type
        )

    finally:
        # Clean up temporary directory
        tempdir.cleanup()

    # Compare with reference metadata if required
    if reference:
        reference_metadata = yaml.safe_load(reference)
        report.compare(reference_metadata)

    # Generate output
    logger.debug(f"Using message level {MessageType(level)}")
    out = report.output(
        OutputType(format),
        level = MessageType(level),
        plain = plain,
        path = output
    )

    # Check if output to a file is requested
    if isinstance(out, str):
        if output:
            # Store output
            with open(output, 'w', encoding='utf-8') as file:
                file.write(out)
        else:
            # Display output
            click.echo(out)

    if metadata:
        out = report.as_dict(plain)['metadata']
        if metadata.name.endswith('.json'):
            metadata.write(json.dumps(out, indent=4))
        else:
            yaml.dump(out, metadata)


if __name__ == '__main__':
    main()