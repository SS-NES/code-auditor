import codescanner
import json
from git import Repo
from tempfile import TemporaryDirectory

import click


@click.command(
    context_settings = {
        'show_default': True,
    }
)
@click.argument(
    'path'
)
@click.option(
    '--debug',
    is_flag = True,
    default = False,
    help = "Enable debug mode."
)
def run(path, debug):
    if path.startswith("http"):
        with TemporaryDirectory() as temppath:
            Repo.clone_from(path, temppath)
            report = codescanner.scan(temppath)

    else:
        report = codescanner.scan(path)

    print(report)


if __name__ == '__main__':
    run()