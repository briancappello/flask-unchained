import networkx as nx

from collections import namedtuple
from importlib import import_module
from typing import *

from ..app_factory_hook import AppFactoryHook
from ..bundles import Bundle
from ..flask_unchained import FlaskUnchained


HookTuple = namedtuple('HookTuple', ('HookClass', 'bundle'))


class RunHooksHook(AppFactoryHook):
    """
    An internal hook to discover and run all the other hooks.
    """

    bundle_module_names = ['hooks']
    """
    The default module this hook loads from.

    Override by setting the ``hooks_module_names`` attribute on your
    bundle class.
    """

    def run_hook(self,
                 app: FlaskUnchained,
                 bundles: List[Bundle],
                 unchained_config: Optional[Dict[str, Any]] = None,
                 ) -> None:
        """
        Collect hooks from Flask Unchained and the list of bundles, resolve their
        correct order, and run them in that order to build (boot) the app instance.
        """
        hook_tuples = self.collect_from_bundles(
            bundles, _initial_objects=self.collect_unchained_hooks())

        for HookClass, bundle in self.resolve_hook_order(hook_tuples):
            hook = HookClass(self.unchained, bundle)
            hook.run_hook(app, bundles, unchained_config)
            hook.update_shell_context(self.unchained._shell_ctx)

    def collect_from_bundle(self, bundle: Bundle) -> Dict[str, HookTuple]:
        """
        Collect hooks from a bundle hierarchy.
        """
        return {hook_class_name: HookTuple(HookClass, bundle)
                for hook_class_name, HookClass
                in super().collect_from_bundle(bundle).items()}

    def collect_unchained_hooks(self) -> Dict[str, HookTuple]:
        """
        Collect hooks built into Flask Unchained that should always run.
        """
        unchained_hooks_pkg = import_module('flask_unchained.hooks')
        return {hook_class_name: HookTuple(HookClass, bundle=None)
                for hook_class_name, HookClass
                in self._collect_from_package(unchained_hooks_pkg).items()}

    def type_check(self, obj: Any) -> bool:
        """
        Returns True if ``obj`` is a subclass of
        :class:`~flask_unchained.AppFactoryHook`.
        """
        is_hook_cls = isinstance(obj, type) and issubclass(obj, AppFactoryHook)
        return is_hook_cls and obj not in {AppFactoryHook, RunHooksHook}

    def resolve_hook_order(self, hook_tuples: Dict[str, HookTuple]) -> List[HookTuple]:
        dag = nx.DiGraph()

        for hook_tuple in hook_tuples.values():
            HookClass, _ = hook_tuple
            dag.add_node(HookClass.name, hook_tuple=hook_tuple)
            for dep_name in HookClass.run_after:
                dag.add_edge(HookClass.name, dep_name)
            for successor_name in HookClass.run_before:
                dag.add_edge(successor_name, HookClass.name)

        try:
            order = reversed(list(nx.topological_sort(dag)))
        except nx.NetworkXUnfeasible:
            msg = 'Circular dependency detected between hooks'
            problem_graph = ', '.join(f'{a} -> {b}'
                                      for a, b in nx.find_cycle(dag))
            raise Exception(f'{msg}: {problem_graph}')

        rv = []
        for hook_name in order:
            hook_tuple = dag.nodes[hook_name].get('hook_tuple')
            if hook_tuple:
                rv.append(hook_tuple)
        return rv
