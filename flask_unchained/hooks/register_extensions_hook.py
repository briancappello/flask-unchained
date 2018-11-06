import networkx as nx

from collections import namedtuple
from typing import *

from ..app_factory_hook import AppFactoryHook
from ..bundle import Bundle
from ..flask_unchained import FlaskUnchained


ExtensionTuple = namedtuple('ExtensionTuple',
                            ('name', 'extension', 'dependencies'))


class RegisterExtensionsHook(AppFactoryHook):
    """
    Registers extensions found in bundles with the ``unchained`` extension.
    """

    bundle_module_name = 'extensions'
    name = 'extensions'

    def run_hook(self, app: FlaskUnchained, bundles: List[Bundle]) -> None:
        extensions = self.collect_from_bundles(bundles)
        self.process_objects(app, self.get_extension_tuples(extensions))

    def process_objects(self,
                        app: FlaskUnchained,
                        extension_tuples: List[ExtensionTuple],
                        ) -> None:
        for ext in self.resolve_extension_order(extension_tuples):
            if ext.name not in self.unchained.extensions:
                self.unchained.extensions[ext.name] = ext.extension

    def get_extension_tuples(self, extensions: Dict[str, object],
                             ) -> List[ExtensionTuple]:
        extension_tuples = []
        for name, extension in extensions.items():
            dependencies = []
            if isinstance(extension, (list, tuple)):
                extension, dependencies = extension
            extension_tuples.append(
                ExtensionTuple(name, extension, dependencies))
        return extension_tuples

    def collect_from_bundle(self, bundle: Bundle) -> Dict[str, object]:
        extensions = {}
        for bundle in bundle._iter_class_hierarchy():
            module = self.import_bundle_module(bundle)
            extensions.update(getattr(module, 'EXTENSIONS', {}))
        return extensions

    def update_shell_context(self, ctx: Dict[str, Any]):
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
            extension_order = reversed(list(nx.topological_sort(dag)))
        except nx.NetworkXUnfeasible:
            msg = 'Circular dependency detected between extensions'
            problem_graph = ', '.join([f'{a} -> {b}'
                                       for a, b in nx.find_cycle(dag)])
            raise Exception(f'{msg}: {problem_graph}')

        rv = []
        for ext_name in extension_order:
            try:
                rv.append(dag.nodes[ext_name]['extension_tuple'])
            except KeyError as e:
                if 'extension_tuple' not in str(e):
                    raise e
                raise Exception(
                    f'Could not locate an extension with the name {ext_name!r}')
        return rv
