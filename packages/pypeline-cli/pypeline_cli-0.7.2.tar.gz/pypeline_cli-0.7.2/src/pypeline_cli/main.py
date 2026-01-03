import click

from .commands.init import init
from .commands.sync_deps import sync_deps
from .commands.install import install
from .commands.create_pipeline import create_pipeline
from .commands.create_processor import create_processor
from .commands.build import build


@click.group()
def cli():
    pass


cli.add_command(init)
cli.add_command(sync_deps)
cli.add_command(install)
cli.add_command(create_pipeline)
cli.add_command(create_processor)
cli.add_command(build)
