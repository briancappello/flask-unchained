from flask_unchained.cli import cli, click

from ..vendor_bundle.commands import foo_group


@foo_group.command()
def bar():
    """override_vendor_bundle docstring"""
    click.echo('override_vendor_bundle')


@foo_group.command()
def baz():
    """override_vendor_bundle docstring"""
    click.echo('override_vendor_bundle')


@cli.command()
def vendor_top_level():
    """override_vendor_bundle docstring"""
    click.echo('override_vendor_bundle')
