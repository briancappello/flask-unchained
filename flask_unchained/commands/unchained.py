import click

from flask.cli import cli, with_appcontext

from ..unchained import unchained
from ..string_utils import title_case
from .utils import print_table


@cli.group('unchained')
def unchained_group():
    """Flask Unchained commands"""


@unchained_group.command()
@with_appcontext
def bundles():
    """List discovered bundles"""
    action_log = unchained.get_action_log('bundle')
    click.echo('=' * 80)
    click.echo('Bundles')
    click.echo('=' * 80)
    print_table([title_case(x) for x in action_log.column_names],
                [item.data for item in action_log.items])


@unchained_group.command()
@with_appcontext
def hooks():
    """List registered hooks"""
    action_log = unchained.get_action_log('hook')
    click.echo('=' * 80)
    click.echo('Hooks')
    click.echo('=' * 80)
    print_table([title_case(x) for x in action_log.column_names],
                [item.data for item in action_log.items])
