import networkx as nx

from collections import namedtuple
from typing import *

from ..app_factory_hook import AppFactoryHook
from ..bundles import Bundle
from ..flask_unchained import FlaskUnchained


ExtensionTuple = namedtuple('ExtensionTuple',
                            ('name', 'extension', 'dependencies'))


class RegisterExtensionsHook(AppFactoryHook):
    """
    Registers extensions found in bundles with the ``unchained`` extension.
    """

    name = 'register_extensions'
    bundle_module_names = ['extensions']

    # skipcq: PYL-W0221 (parameters mismatch in overridden method)
    def process_objects(self,
                        app: FlaskUnchained,
                        extensions: Dict[str, object],
                        ) -> None:
        for ext in self.resolve_extension_order(extensions):
            if ext.name not in self.unchained.extensions:
                self.unchained.extensions[ext.name] = ext.extension

    def collect_from_bundle(self, bundle: Bundle) -> Dict[str, object]:
        extensions = {}
        for b in bundle._iter_class_hierarchy():
            for module in self.import_bundle_modules(b):
                extensions.update(getattr(module, 'EXTENSIONS', {}))
        return extensions

    def update_shell_context(self, ctx: Dict[str, Any]) -> None:
        ctx.update(self.unchained.extensions)

    def resolve_extension_order(self,
                                extensions: Dict[str, object],
                                ) -> List[ExtensionTuple]:
        extension_tuples = []
        for name, extension in extensions.items():
            dependencies = []
            if isinstance(extension, (list, tuple)):
                extension, dependencies = extension
            extension_tuples.append(ExtensionTuple(name, extension, dependencies))

        dag = nx.DiGraph()
        for ext in extension_tuples:
            dag.add_node(ext.name, extension_tuple=ext)
            for dep_name in ext.dependencies:
                dag.add_edge(ext.name, dep_name)

        try:
            extension_order = reversed(list(nx.topological_sort(dag)))
        except nx.NetworkXUnfeasible:
            msg = 'Circular dependency detected between extensions'
            problem_graph = ', '.join(f'{a} -> {b}'
                                      for a, b in nx.find_cycle(dag))
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
