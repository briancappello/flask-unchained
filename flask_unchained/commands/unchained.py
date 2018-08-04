from flask_unchained.cli import cli, click

from ..unchained import unchained
from ..string_utils import title_case
from .utils import print_table


@cli.group('unchained')
def unchained_group():
    """
    Flask Unchained commands.
    """


@unchained_group.command()
def bundles():
    """
    List discovered bundles.
    """
    action_log = unchained.get_action_log('bundle')
    click.echo('=' * 80)
    click.echo('Bundles')
    click.echo('=' * 80)
    print_table([title_case(x) for x in action_log.column_names],
                [item.data for item in action_log.items])


@unchained_group.command()
def hooks():
    """
    List registered hooks (in the order they run).
    """
    action_log = unchained.get_action_log('hook')
    click.echo('=' * 80)
    click.echo('Hooks')
    click.echo('=' * 80)
    print_table([title_case(x) for x in action_log.column_names],
                [item.data for item in action_log.items])
