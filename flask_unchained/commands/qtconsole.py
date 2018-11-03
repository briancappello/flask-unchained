"""
Launch the QtConsole GUI with the Flask app context embedded. **!!EXPERIMENTAL!!**
"""
import errno
import multiprocessing
import os
import sys
import tempfile
import time

from flask_unchained.cli import click, with_appcontext

from .shell import _get_shell_banner, _get_shell_ctx

try:
    from IPython.utils import io
    from IPython.utils.frame import extract_module_locals
    from ipykernel.kernelapp import IPKernelApp
    from PyQt5 import QtGui, QtWidgets
    from qtconsole import qtconsoleapp
    from qtconsole.manager import QtKernelManager
    from qtconsole.rich_jupyter_widget import RichJupyterWidget

# don't register the command if IPython and/or qtconsole aren't installed
except ImportError:
    from py_meta_utils import OptionalClass as IPKernelApp
    from py_meta_utils import OptionalClass as QtWidgets
    from py_meta_utils import OptionalClass as RichJupyterWidget

    class cli:
        @staticmethod
        def command(*args, **kwargs):
            return lambda fn: None


@click.command()
@with_appcontext
def qtconsole():
    """
    Starts qtconsole in the app context. **!!EXPERIMENTAL!!**

    Only available if ``Ipython``, ``PyQt5`` and ``qtconsole`` are installed.
    """
    connection_file = os.path.join(tempfile.gettempdir(),
                                   f'connection-{os.getpid()}.json')
    p = multiprocessing.Process(target=launch_qtconsole,
                                args=(connection_file,))
    try:
        p.start()
        embed_kernel(local_ns=_get_shell_ctx(),
                     connection_file=connection_file)
        p.join()
    finally:
        try:
            os.unlink(connection_file)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise


def launch_qtconsole(connection_file):
    wait_for_connection_file(connection_file)

    app = QtWidgets.QApplication([])
    app._kernel_has_shutdown = False

    kernel_manager = QtKernelManager()
    kernel_manager.load_connection_file(connection_file)

    kernel_client = kernel_manager.client()
    kernel_client.start_channels()

    jupyter_widget = JupyterWidget()
    jupyter_widget.kernel_manager = kernel_manager
    jupyter_widget.kernel_client = kernel_client

    window = MainWindow(jupyter_widget)
    window.show()

    def shutdown_kernel():
        if app._kernel_has_shutdown:
            return

        jupyter_widget.kernel_client.stop_channels()
        jupyter_widget.kernel_manager.shutdown_kernel()
        app._kernel_has_shutdown = True
        app.exit()

    jupyter_widget.exit_requested.connect(shutdown_kernel)
    app.aboutToQuit.connect(shutdown_kernel)

    return app.exec_()


class JupyterWidget(RichJupyterWidget):
    def __init__(self):
        super().__init__()
        self.banner = _get_shell_banner()

    def reset(self, clear=False):
        """
        Overridden to customize the order that the banners are printed
        """
        if self._executing:
            self._executing = False
            self._request_info['execute'] = {}
        self._reading = False
        self._highlighter.highlighting_on = False

        if clear:
            self._control.clear()
            if self._display_banner:
                if self.kernel_banner:
                    self._append_plain_text(self.kernel_banner)
                self._append_plain_text(self.banner)

        # update output marker for stdout/stderr, so that startup
        # messages appear after banner:
        self._show_interpreter_prompt()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, jupyter_widget):
        super().__init__()
        self.setCentralWidget(jupyter_widget)
        self.setWindowTitle('Flask QtConsole')

        base_path = os.path.abspath(os.path.dirname(qtconsoleapp.__file__))
        icon_path = os.path.join(base_path, 'resources', 'icon', 'JupyterConsole.svg')
        icon = QtGui.QIcon(icon_path)
        self.setWindowIcon(icon)


class IPythonKernelApp(IPKernelApp):
    def log_connection_info(self):
        """
        Overridden to customize the start-up message printed to the terminal
        """
        _ctrl_c_lines = [
            'NOTE: Ctrl-C does not work to exit from the command line.',
            'To exit, just close the window, type "exit" or "quit" at the '
            'qtconsole prompt, or use Ctrl-\\ in UNIX-like environments '
            '(at the command prompt).']

        for line in _ctrl_c_lines:
            io.rprint(line)

        # upstream has this here, even though it seems like a silly place for it
        self.ports = dict(shell=self.shell_port, iopub=self.iopub_port,
                          stdin=self.stdin_port, hb=self.hb_port,
                          control=self.control_port)


def embed_kernel(module=None, local_ns=None, **kwargs):
    """Embed and start an IPython kernel in a given scope.

    This code is an exact copy of the IPython.embed.embed_kernel function,
    except it uses our IPythonKernelApp subclass of IPKernelApp (so that we can
    customize the start-up error message about Ctrl-C not working because of a
    technicality in how IPython works)
    """
    # get the app if it exists, or set it up if it doesn't
    if IPythonKernelApp.initialized():
        app = IPythonKernelApp.instance()
    else:
        app = IPythonKernelApp.instance(**kwargs)
        app.initialize([])
        # Undo unnecessary sys module mangling from init_sys_modules.
        # This would not be necessary if we could prevent it
        # in the first place by using a different InteractiveShell
        # subclass, as in the regular embed case.
        main = app.kernel.shell._orig_sys_modules_main_mod
        if main is not None:
            sys.modules[app.kernel.shell._orig_sys_modules_main_name] = main

    # load the calling scope if not given
    (caller_module, caller_locals) = extract_module_locals(1)
    if module is None:
        module = caller_module
    if local_ns is None:
        local_ns = caller_locals

    app.kernel.user_module = module
    app.kernel.user_ns = local_ns
    app.shell.set_completer_frame()
    app.start()


def wait_for_connection_file(connection_file):
    for i in range(100):
        try:
            st = os.stat(connection_file)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise
        else:
            if st.st_size > 0:
                break
        time.sleep(0.1)
