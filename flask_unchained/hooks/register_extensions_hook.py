"""
extension dependency resolution order code adapted from:
https://www.electricmonk.nl/log/2008/08/07/dependency-resolving-algorithm/
"""
import inspect

from collections import namedtuple
from typing import List

from flask import Flask

from ..app_factory_hook import AppFactoryHook


ExtensionTuple = namedtuple('ExtensionTuple',
                            ('name', 'extension', 'dependencies'))

PARENT_NODE = '__parent__'


class Node:
    def __init__(self, name, extension, dependencies):
        self.name = name
        self.extension = extension
        self.dependencies = dependencies
        self.dependent_nodes = []

    def add_dependent_node(self, node):
        self.dependent_nodes.append(node)


class RegisterExtensionsHook(AppFactoryHook):
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

    def type_check(self, obj):
        return not inspect.isclass(obj) and hasattr(obj, 'init_app')

    def collect_from_bundle(self, bundle):
        module = self.import_bundle_module(bundle)
        if not module:
            return []

        return self.get_extension_tuples(getattr(module, 'EXTENSIONS', {}))

    def process_objects(self, app: Flask, extension_tuples):
        for ext in self.resolve_extension_order(extension_tuples):
            self.log_action(ext)
            ext.extension.init_app(app)
            self.unchained._extensions[ext.name] = ext.extension

    def get_extension_tuples(self, extensions: dict):
        extension_tuples = []
        for name, extension in extensions.items():
            if isinstance(extension, (list, tuple)):
                extension, dependencies = extension
            else:
                dependencies = []
            extension_tuples.append(
                ExtensionTuple(name, extension, dependencies))
        return extension_tuples

    def update_shell_context(self, ctx: dict):
        ctx.update(self.unchained._extensions)
        ctx.update({'unchained': self.unchained})

    def resolve_extension_order(self, extensions: List[ExtensionTuple]):
        nodes = {}
        for ext in extensions:
            nodes[ext.name] = Node(*ext)

        parent_node = Node(PARENT_NODE, None, list(nodes.keys()))
        nodes[PARENT_NODE] = parent_node

        for name, node in nodes.items():
            for dep_name in node.dependencies:
                node.add_dependent_node(nodes[dep_name])

        order = []
        self._resolve_dependencies(parent_node, order, [])
        return [node for node in order if node.name != PARENT_NODE]

    def _resolve_dependencies(self, node: Node, resolved, unresolved):
        unresolved.append(node)
        for dep_node in node.dependent_nodes:
            if dep_node not in resolved:
                if dep_node in unresolved:
                    raise Exception(
                        f'Circular dependency detected: {dep_node.name} '
                        f'depends on an extension that depends on it.')
                self._resolve_dependencies(dep_node, resolved, unresolved)
        resolved.append(node)
        unresolved.remove(node)
