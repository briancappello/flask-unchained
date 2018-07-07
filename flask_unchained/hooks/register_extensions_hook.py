import inspect
import networkx as nx

from collections import namedtuple
from flask import Flask
from typing import *

from ..app_factory_hook import AppFactoryHook
from ..bundle import Bundle


ExtensionTuple = namedtuple('ExtensionTuple',
                            ('name', 'extension', 'dependencies'))


class RegisterExtensionsHook(AppFactoryHook):
    """
    Registers extensions found in bundles with the current app.
    """
    bundle_module_name = 'extensions'
    name = 'extensions'

    action_category = 'extensions'
    action_table_columns = ['name', 'class', 'dependencies']
    action_table_converter = lambda ext: [ext.name,
                                          ext.extension.__class__.__name__,
                                          ext.dependencies]

    def run_hook(self, app: Flask, bundles: List[Type[Bundle]]):
        extensions = self.collect_from_bundles(bundles)
        self.process_objects(app, self.get_extension_tuples(extensions))

    def collect_from_bundle(self, bundle: Type[Bundle]):
        extensions = {}
        for bundle in bundle.iter_class_hierarchy():
            module = self.import_bundle_module(bundle)
            extensions.update(getattr(module, 'EXTENSIONS', {}))
        return extensions

    def process_objects(self, app: Flask,
                        extension_tuples: List[ExtensionTuple]):
        for ext in self.resolve_extension_order(extension_tuples):
            self.log_action(ext)
            if ext.name not in self.unchained.extensions:
                self.unchained.extensions[ext.name] = ext.extension

    def get_extension_tuples(self, extensions: dict):
        extension_tuples = []
        for name, extension in extensions.items():
            dependencies = []
            if isinstance(extension, (list, tuple)):
                extension, dependencies = extension
            extension_tuples.append(
                ExtensionTuple(name, extension, dependencies))
        return extension_tuples

    def update_shell_context(self, ctx: dict):
        ctx.update(self.unchained.extensions)
        ctx.update({'unchained': self.unchained})

    def resolve_extension_order(self, extensions: List[ExtensionTuple],
                                ) -> List[ExtensionTuple]:
        dag = nx.DiGraph()
        for ext in extensions:
            dag.add_node(ext.name, extension_tuple=ext)
            for dep_name in ext.dependencies:
                dag.add_edge(ext.name, dep_name)

        try:
            return [dag.nodes[ext_name]['extension_tuple']
                    for ext_name in reversed(list(nx.topological_sort(dag)))]
        except nx.NetworkXUnfeasible:
            msg = 'Circular dependency detected between extensions'
            problem_graph = ', '.join([f'{a} -> {b}'
                                       for a, b in nx.find_cycle(dag)])
            raise Exception(f'{msg}: {problem_graph}')

    def type_check(self, obj):
        return not inspect.isclass(obj) and hasattr(obj, 'init_app')
