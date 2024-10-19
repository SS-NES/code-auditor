import codescanner
from codescanner.analyser import AnalyserType

from git import Repo
from tempfile import TemporaryDirectory

import click

import logging
logger = logging.getLogger(__name__)


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
    '-S',
    '--skip',
    type = click.Choice(
        [
            *codescanner.get_analysers().keys(),
            *codescanner.get_aggregators().keys()
        ],
        case_sensitive = False
    ),
    multiple = True,
    help = "List of analysers to skip."
)
@click.option(
    '-T',
    '--skip-type',
    type = click.Choice(
        [item.value for item in AnalyserType],
        case_sensitive = False
    ),
    multiple = True,
    help = "List of analysers types to skip."
)
@click.option(
    '-p',
    '--smp',
    type = click.File("r", encoding="utf-8"),
    help = "Path of the software management plan (SMP) for comparison."
)
# Remote repository options
@click.option(
    '-b',
    '--branch',
    type = click.STRING,
    help = "Branch or tag of the remote code repository."
)
# Output options
@click.option(
    '-m',
    '--metadata',
    type = click.File("w", encoding="utf-8", lazy=True),
    help = "Path to store the metadata extracted from the code base."
)
@click.option(
    '-o',
    '--output',
    type = click.File("w", encoding="utf-8", lazy=True),
    help = "Path to store the analysis output."
)
@click.option(
    '-f',
    '--format',
    type = click.Choice(['text', 'json', 'yaml'], case_sensitive = False),
    default = 'text',
    help = "Output format."
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
    skip,
    skip_type,
    smp,
    branch,
    metadata,
    output,
    format,
    debug,
):
    """Runs the command line interface (CLI).

    Args:
        path (str): Path of the code base.
        skip (list[str]): List of analysers to skip (optional).
        skip_type (list[str]): List of analyser types to skip (optional).
        smp (str): Path of the software management plan (SMP) (optional).
        branch (str): Branch or tag of the remote repository (optional).
        metadata (str): Path to store the metadata extracted from the code base (optional).
        output (str): Path to store the analysis output (optional).
        format (str): Output format (default = 'text').
        debug (bool): Debug flag (default = False).
    """
    # Set logging level if debug flag is set
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logger.info("Debugging enabled.")

    # Check if path is a URL address
    if path.startswith('http'):

        # Clone repository to a temporary directory and analyse the code base
        logger.info(f"Cloning `{path}`.")
        with TemporaryDirectory() as temppath:
            Repo.clone_from(path, temppath, branch=branch)
            report = codescanner.analyse(temppath, skip, skip_type)

    else:
        # Analyse the code base
        report = codescanner.analyse(path, skip, skip_type)

    if format == "text":
        click.echo(report)

    elif format == "json":
        # TODO: JSON output
        pass

    elif format == "yaml":
        # TODO: Yaml output
        pass

    if metadata:
        # TODO: Store metadata
        pass


if __name__ == '__main__':
    main()