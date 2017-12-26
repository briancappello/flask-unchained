import click

from flask.cli import with_appcontext

from ..unchained import unchained as unchained_store
from ..utils import title_case
from .utils import print_table


@click.group()
def unchained():
    """Flask Unchained commands"""


@unchained.command()
@with_appcontext
def bundles():
    """List discovered bundles"""
    action_log = unchained_store.get_action_log('bundle')
    click.echo('=' * 80)
    click.echo('Bundles')
    click.echo('=' * 80)
    print_table([title_case(x) for x in action_log.column_names],
                [item.data for item in action_log.items])


@unchained.command()
@with_appcontext
def hooks():
    """List registered hooks"""
    action_log = unchained_store.get_action_log('hook')
    click.echo('=' * 80)
    click.echo('Hooks')
    click.echo('=' * 80)
    print_table([title_case(x) for x in action_log.column_names],
                [item.data for item in action_log.items])
