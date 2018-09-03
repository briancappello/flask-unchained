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
    from ..app_factory import _load_bundles, _load_unchained_config
    unchained_config = _load_unchained_config(ctx.obj.data['env'])
    _, bundles = _load_bundles(getattr(unchained_config, 'BUNDLES', []))

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
    from ..app_factory import _load_bundles, _load_unchained_config
    unchained_config = _load_unchained_config(ctx.obj.data['env'])
    _, bundles = _load_bundles(getattr(unchained_config, 'BUNDLES', []))
    hooks = RunHooksHook(None).collect_from_bundles(bundles)

    print_table(('Hook Name',
                 'Default Bundle Module',
                 'Bundle Module Override Attr',
                 'Description'),
                [(hook.name,
                 hook.bundle_module_name or '(None)',
                 hook.bundle_override_module_name_attr or '(None)',
                 format_docstring(hook.__doc__) or '(None)') for hook in hooks])
