import networkx as nx

from collections import namedtuple
from typing import *

from .register_extensions_hook import RegisterExtensionsHook
from ..flask_unchained import FlaskUnchained


ExtensionTuple = namedtuple('ExtensionTuple',
                            ('name', 'extension', 'dependencies'))


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
        for extension_tuple in self.resolve_extension_order(extensions):
            name, extension, _ = extension_tuple
            if name in self.unchained.extensions:
                extension = self.unchained.extensions[name]

            extension.init_app(app)
            if name not in self.unchained.extensions:
                self.unchained.extensions[name] = extension

    def update_shell_context(self, ctx: Dict[str, Any]) -> None:
        """
        Add extensions to the CLI shell context.
        """
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
        for extension_tuple in extension_tuples:
            dag.add_node(extension_tuple.name, extension_tuple=extension_tuple)
            for dep_name in extension_tuple.dependencies:
                dag.add_edge(extension_tuple.name, dep_name)

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
                raise Exception(f'Could not locate extension named {ext_name!r}')
        return rv
