import os
import sys
import traceback

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
    # We want to honor both $PYTHONSTARTUP and .pythonrc.py, so follow system
    # conventions and get $PYTHONSTARTUP first then .pythonrc.py.
    for pythonrc in [os.environ.get("PYTHONSTARTUP"),
                     os.path.expanduser('~/.pythonrc.py')]:
        if not pythonrc or not os.path.isfile(pythonrc):
            continue
        with open(pythonrc) as f:
            pythonrc_code = f.read()
        # Match the behavior of the cpython shell where an error in
        # PYTHONSTARTUP prints an exception and continues.
        try:
            exec(compile(pythonrc_code, pythonrc, 'exec'), ctx)  # skipcq: PYL-W0122
        except:
            traceback.print_exc()

    ctx.update(app.make_shell_context())
    return ctx
