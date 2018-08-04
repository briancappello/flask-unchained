from flask_unchained.cli import cli, click

from ..vendor_bundle.commands import foo_group


@foo_group.command()
def baz():
    """myapp docstring"""
    click.echo('myapp')


@click.group()
def goo_group():
    """myapp docstring"""


@goo_group.command()
def gar():
    click.echo('myapp')


@cli.command()
def top_level():
    click.echo('myapp')
