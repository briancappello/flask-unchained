from flask import Flask
from typing import *

from .register_extensions_hook import ExtensionTuple, RegisterExtensionsHook


class InitExtensionsHook(RegisterExtensionsHook):
    """
    Initializes extensions found in bundles with the current app.
    """
    action_category = 'extensions'
    action_table_columns = ['name', 'class', 'dependencies']
    action_table_converter = lambda ext: [ext.name,
                                          ext.extension.__class__.__name__,
                                          ext.dependencies]
    bundle_module_name = 'extensions'
    name = 'extensions'
    priority = 60

    def process_objects(self, app: Flask,
                        extension_tuples: List[ExtensionTuple]):
        for ext in self.resolve_extension_order(extension_tuples):
            ext.extension.init_app(app)
            self.unchained.extensions[ext.name] = ext.extension
