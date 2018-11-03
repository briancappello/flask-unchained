from flask_unchained.cli import click

from ..utils import format_docstring
from .utils import print_table


@click.group('unchained')
def unchained_group():
    """
    Flask Unchained commands.
    """


@unchained_group.command()
@click.pass_context
def bundles(ctx):
    """
    List discovered bundles.
    """
    bundles = _get_bundles(ctx.obj.data['env'])
    print_table(('Name', 'Location'),
                [(bundle.name, f'{bundle.__module__}.{bundle.__class__.__name__}')
                 for bundle in bundles])


@unchained_group.command()
@click.pass_context
def hooks(ctx):
    """
    List registered hooks (in the order they run).
    """
    from ..hooks.run_hooks_hook import RunHooksHook

    bundles = _get_bundles(ctx.obj.data['env'])
    hooks = RunHooksHook(None).collect_from_bundles(bundles)
    print_table(('Hook Name',
                 'Default Bundle Module',
                 'Bundle Module Override Attr',
                 'Description'),
                [(hook.name,
                 hook.bundle_module_name or '(None)',
                 hook.bundle_override_module_name_attr or '(None)',
                 format_docstring(hook.__doc__) or '(None)') for hook in hooks])


def _get_bundles(env):
    from ..app_factory import _load_bundles, _load_unchained_config

    unchained_config = _load_unchained_config(env)
    return _load_bundles(getattr(unchained_config, 'BUNDLES', []))[1]
