import os
import sys

from flask_unchained.cli import click, with_appcontext
from flask.globals import _app_ctx_stack


@click.command()
@with_appcontext
def shell():
    """
    Runs a shell in the app context. If ``IPython`` is installed, it will
    be used, otherwise the default Python shell is used.
    """
    ctx = _get_shell_ctx()
    try:
        import IPython
        IPython.embed(header=_get_shell_banner(), user_ns=ctx)
    except ImportError:
        import code
        code.interact(banner=_get_shell_banner(verbose=True), local=ctx)


def _get_shell_banner(verbose=False):
    app = _app_ctx_stack.top.app
    py_version = sys.version.replace('\n', '')
    python = f'Python {py_version} on {sys.platform}'
    flask_app = f"Flask App: {app.import_name}{app.debug and ' [debug]' or ''}"
    return verbose and '\n'.join([python, flask_app]) or flask_app


def _get_shell_ctx():
    app = _app_ctx_stack.top.app
    ctx = {}

    # Support the regular Python interpreter startup script if someone is using it.
    startup = os.environ.get('PYTHONSTARTUP')
    if startup and os.path.isfile(startup):
        with open(startup, 'r') as f:
            eval(compile(f.read(), startup, 'exec'), ctx)

    ctx.update(app.make_shell_context())
    return ctx
