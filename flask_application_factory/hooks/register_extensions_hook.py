"""
extension dependency resolution order code adapted from:
https://www.electricmonk.nl/log/2008/08/07/dependency-resolving-algorithm/
"""
import inspect

from collections import namedtuple
from flask import Flask
from typing import List

from ..factory_hook import FactoryHook


ExtensionTuple = namedtuple('ExtensionTuple', ('name', 'extension', 'dependencies'))

PARENT_NODE = '__parent__'


class Node:
    def __init__(self, name, dependencies):
        self.name = name
        self.dependencies = dependencies
        self.dependent_nodes = []

    def add_dependent_node(self, node):
        self.dependent_nodes.append(node)

    def __repr__(self):
        return f'{self.name}: {self.dependencies!r}'


class RegisterExtensionsHook(FactoryHook):
    priority = 10
    bundle_module_name = 'extensions'
    extensions = {}

    def type_check(self, obj):
        return not inspect.isclass(obj) and hasattr(obj, 'init_app')

    def collect_from_bundle(self, bundle):
        module = self.import_bundle_module(bundle)
        if not module:
            return []

        return self.get_extension_tuples(getattr(module, 'EXTENSIONS', {}))

    def process_objects(self, app: Flask, app_config_cls, objects):
        order = self.resolve_extension_order(objects)
        extensions = {ext.name: ext.extension for ext in objects}
        for name in order:
            extensions[name].init_app(app)
        self.extensions.update(extensions)

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
        ctx.update(self.extensions)

    def resolve_extension_order(self, extensions: List[ExtensionTuple]):
        nodes = {}
        for extension in extensions:
            nodes[extension.name] = Node(extension.name, extension.dependencies)

        parent_node = Node(PARENT_NODE, list(nodes.keys()))
        nodes[PARENT_NODE] = parent_node

        for name, node in nodes.items():
            for dependency_name in node.dependencies:
                try:
                    node.add_dependent_node(nodes[dependency_name])
                except KeyError as e:
                    if dependency_name not in self.extensions:
                        raise e

        order = []
        self._resolve_dependencies(parent_node, order, [])
        return [node.name for node in order if node.name != PARENT_NODE]

    def _resolve_dependencies(self, node: Node, resolved: list, unresolved: list):
        unresolved.append(node)
        for dependent_node in node.dependent_nodes:
            if dependent_node not in resolved:
                if dependent_node in unresolved:
                    raise Exception(
                        f'Circular dependency detected: {dependent_node.name} '
                        f'depends on an extension that depends on it.')
                self._resolve_dependencies(dependent_node, resolved, unresolved)
        resolved.append(node)
        unresolved.remove(node)
