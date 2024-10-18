import codescanner

import json
from git import Repo
from tempfile import TemporaryDirectory

import click
import logging


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
    '--debug',
    is_flag = True,
    default = False,
    help = "Enable debug mode."
)
def main(path, debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    if path.startswith('http'):
        with TemporaryDirectory() as temppath:
            Repo.clone_from(path, temppath)
            report = codescanner.scan(temppath)

    else:
        report = codescanner.scan(path)

    print(report)


if __name__ == '__main__':
    main()