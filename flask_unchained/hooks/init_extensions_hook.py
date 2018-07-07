from flask import Flask
from typing import *

from .register_extensions_hook import ExtensionTuple, RegisterExtensionsHook


class InitExtensionsHook(RegisterExtensionsHook):
    """
    Initializes extensions found in bundles with the current app.
    """
    bundle_module_name = 'extensions'
    name = 'init_extensions'
    run_after = ['extensions']

    action_category = 'extensions'
    action_table_columns = ['name', 'class', 'dependencies']
    action_table_converter = lambda ext: [ext.name,
                                          ext.extension.__class__.__name__,
                                          ext.dependencies]

    def process_objects(self, app: Flask,
                        extension_tuples: List[ExtensionTuple]):
        for ext in self.resolve_extension_order(extension_tuples):
            instance = self.unchained.extensions.get(ext.name, ext.extension)
            instance.init_app(app)
            if ext.name not in self.unchained.extensions:
                self.unchained.extensions[ext.name] = instance
