from typing import *

from .register_extensions_hook import ExtensionTuple, RegisterExtensionsHook
from ..flask_unchained import FlaskUnchained


class InitExtensionsHook(RegisterExtensionsHook):
    """
    Initializes extensions found in bundles with the current app.
    """

    bundle_module_name = 'extensions'
    name = 'init_extensions'
    run_after = ['extensions']

    def process_objects(self,
                        app: FlaskUnchained,
                        extension_tuples: List[ExtensionTuple],
                        ) -> None:
        for ext in self.resolve_extension_order(extension_tuples):
            ext_instance = (ext.extension if ext.name not in self.unchained.extensions
                            else self.unchained.extensions[ext.name])
            ext_instance.init_app(app)
            if ext.name not in self.unchained.extensions:
                self.unchained.extensions[ext.name] = ext_instance
