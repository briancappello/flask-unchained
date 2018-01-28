import inspect
import networkx as nx

from collections import namedtuple
from typing import List

from flask import Flask

from ..app_factory_hook import AppFactoryHook


ExtensionTuple = namedtuple('ExtensionTuple',
                            ('name', 'extension', 'dependencies'))


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
        dag = nx.DiGraph()
        for ext in extensions:
            dag.add_node(ext.name, extension_tuple=ext)
            for dep_name in ext.dependencies:
                dag.add_edge(ext.name, dep_name)

        try:
            return [dag.nodes[n]['extension_tuple']
                    for n in reversed(list(nx.topological_sort(dag)))]
        except nx.NetworkXUnfeasible:
            msg = 'Circular dependency detected between extensions'
            problem_graph = ', '.join([f'{a} -> {b}'
                                       for a, b in nx.find_cycle(dag)])
            raise Exception(f'{msg}: {problem_graph}')
