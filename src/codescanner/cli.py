import codescanner

from git import Repo
from tempfile import TemporaryDirectory

import click

import logging
logger = logging.getLogger(__name__)


@click.command(
    context_settings = {
        'show_default': True,
    },
    help = "Scans the code base, where PATH is the path of the code base."
)
@click.argument(
    'path',
)
@click.option(
    '--skip',
    multiple = True,
    help = "List of analysers to skip."
)
@click.option(
    '--skip-type',
    multiple = True,
    help = "List of analysers types to skip."
)
@click.option(
    '--debug',
    is_flag = True,
    default = False,
    help = "Enable debug mode."
)
def main(path, debug, skip, skip_type):
    """Runs the command line interface (CLI).

    Args:
        path (str): Path of the code base.
        debug (bool): Debug flag (default = False)
    """
    # Set logging level if debug flag is set
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    # Check if path is a URL address
    if path.startswith('http'):

        # Clone repository to a temporary directory and analyse the code base
        with TemporaryDirectory() as temppath:
            Repo.clone_from(path, temppath)
            report = codescanner.analyse(temppath, skip, skip_type)

    else:
        # Analyse the code base
        report = codescanner.analyse(path, skip, skip_type)

    print(report)


if __name__ == '__main__':
    main()