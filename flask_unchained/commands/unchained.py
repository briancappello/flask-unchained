from flask_unchained import current_app
from flask_unchained.cli import cli, click, print_table

from ..utils import format_docstring


@cli.group('unchained')
def unchained_group():
    """
    Flask Unchained commands.
    """


@unchained_group.command()
def bundles():
    """
    List registered bundles.
    """
    header = ('Name', 'Location')
    rows = [(bundle.name, f'{bundle.__module__}.{bundle.__class__.__name__}')
            for bundle in current_app.unchained.bundles.values()]
    print_table(header, rows)


@unchained_group.command()
@click.argument('bundle_name', nargs=1, required=False, default=None,
                help='Only show options for a specific bundle.')
def config(bundle_name):
    """
    Show current app config (or optionally just the options for a specific bundle).
    """
    from ..hooks import ConfigureAppHook

    bundle = current_app.unchained.bundles[bundle_name] if bundle_name else None
    bundle_cfg = (ConfigureAppHook(None).get_bundle_config(bundle, current_app.env)
                  if bundle else None)

    header = ('Config Key', 'Value')
    rows = []
    for key, value in current_app.config.items():
        if not bundle or key in bundle_cfg:
            rows.append((key, str(value)))
    print_table(header, rows)


@unchained_group.command()
def extensions():
    """
    List extensions.
    """
    header = ('Name', 'Class', 'Location')
    rows = []
    for name, ext in current_app.unchained.extensions.items():
        ext = ext if not isinstance(ext, tuple) else ext[0]
        rows.append((name, ext.__class__.__name__, ext.__module__))
    print_table(header, sorted(rows, key=lambda row: row[0]))


@unchained_group.command()
@click.pass_context
def hooks(ctx):
    """
    List registered hooks (in the order they run).
    """
    from ..app_factory import AppFactory
    from ..hooks.run_hooks_hook import RunHooksHook

    unchained_config = AppFactory().load_unchained_config(ctx.obj.data['env'])
    _, bundles = AppFactory().load_bundles(getattr(unchained_config, 'BUNDLES', []))
    hooks = RunHooksHook(None).collect_from_bundles(bundles)

    header = ('Hook Name',
              'Default Bundle Module(s)',
              'Bundle Module(s) Override Attr',
              'Description')
    rows = []
    for hook in hooks:
        bundle_module_names = ([hook.bundle_module_name]
                               if hook.require_exactly_one_bundle_module
                               else hook.bundle_module_names)
        rows.append((
            hook.name,
            bundle_module_names and ', '.join(bundle_module_names) or '(None)',
            hook.bundle_override_module_names_attr or '(None)',
            format_docstring(hook.__doc__) or '(None)',
        ))
    print_table(header, rows)


@unchained_group.command()
def services():
    """
    List services.
    """
    header = ('Name', 'Class', 'Location')
    rows = []
    for name, svc in current_app.unchained.services.items():
        if isinstance(svc, object):
            rows.append((name, svc.__class__.__name__, svc.__module__))
        elif hasattr(svc, '__module__') and hasattr(svc, '__name__'):
            rows.append((name, svc.__name__, svc.__module__))
        else:
            rows.append((name, str(svc), ''))

    # sort by name within (grouped by) location
    print_table(
        header,
        sorted(
            sorted(rows, key=lambda row: row[0]),
            key=lambda row: row[2]
        )
    )
