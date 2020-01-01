from typing import *

from .register_extensions_hook import RegisterExtensionsHook
from ..flask_unchained import FlaskUnchained


class InitExtensionsHook(RegisterExtensionsHook):
    """
    Initializes extensions found in bundles with the current app.
    """

    name = 'init_extensions'
    """
    The name of this hook.
    """

    bundle_module_names = ['extensions']
    """
    The default module this hook loads from.

    Override by setting the ``extensions_module_names`` attribute on your
    bundle class.
    """

    run_after = ['register_extensions']

    def process_objects(self,
                        app: FlaskUnchained,
                        extensions: Dict[str, object],
                        ) -> None:
        """
        Initialize each extension with ``extension.init_app(app)``.
        """
        for ext in self.resolve_extension_order(extensions):
            ext_instance = (ext.extension if ext.name not in self.unchained.extensions
                            else self.unchained.extensions[ext.name])
            ext_instance.init_app(app)
            if ext.name not in self.unchained.extensions:
                self.unchained.extensions[ext.name] = ext_instance

    def update_shell_context(self, ctx: Dict[str, Any]) -> None:
        """
        Add extensions to the CLI shell context.
        """
        ctx.update(self.unchained.extensions)
