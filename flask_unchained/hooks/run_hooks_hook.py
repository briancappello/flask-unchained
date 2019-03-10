import networkx as nx

from collections import namedtuple
from importlib import import_module
from typing import *

from ..app_factory_hook import AppFactoryHook
from ..bundle import Bundle
from ..flask_unchained import FlaskUnchained


HookTuple = namedtuple('HookTuple', ('Hook', 'bundle'))


class RunHooksHook(AppFactoryHook):
    """
    An internal hook to discover and run all the other hooks.
    """

    bundle_module_name = 'hooks'

    def run_hook(self,
                 app: FlaskUnchained,
                 bundles: List[Bundle],
                 _config_overrides: Optional[Dict[str, Any]] = None,
                 ) -> None:
        from flask_unchained.hooks.configure_app_hook import ConfigureAppHook

        for hook in self.collect_from_bundles(bundles):
            if isinstance(hook, ConfigureAppHook):
                hook.run_hook(app, bundles, _config_overrides=_config_overrides)
            else:
                hook.run_hook(app, bundles)
            hook.update_shell_context(self.unchained._shell_ctx)

    def collect_from_bundles(self, bundles: List[Bundle]) -> List[AppFactoryHook]:
        hooks = self.collect_from_unchained()
        for bundle in bundles:
            hooks += self.collect_from_bundle(bundle)
        return [hook_tuple.Hook(self.unchained, hook_tuple.bundle)
                for hook_tuple in self.resolve_hook_order(hooks)]

    def collect_from_unchained(self) -> List[HookTuple]:
        hooks_pkg = import_module('flask_unchained.hooks')
        return [HookTuple(Hook, None)
                for Hook in self._collect_from_package(hooks_pkg).values()]

    def collect_from_bundle(self, bundle: Bundle) -> List[HookTuple]:
        return [HookTuple(Hook, bundle)
                for Hook in super().collect_from_bundle(bundle).values()]

    def type_check(self, obj: Any) -> bool:
        is_class = isinstance(obj, type) and issubclass(obj, AppFactoryHook)
        return is_class and obj not in {AppFactoryHook, RunHooksHook}

    def resolve_hook_order(self, hook_tuples: List[HookTuple]) -> List[HookTuple]:
        dag = nx.DiGraph()

        for hook_tuple in hook_tuples:
            dag.add_node(hook_tuple.Hook.name, hook_tuple=hook_tuple)
            for dep_name in hook_tuple.Hook.run_after:
                dag.add_edge(hook_tuple.Hook.name, dep_name)
            for successor_name in hook_tuple.Hook.run_before:
                dag.add_edge(successor_name, hook_tuple.Hook.name)

        try:
            order = reversed(list(nx.topological_sort(dag)))
        except nx.NetworkXUnfeasible:
            msg = 'Circular dependency detected between hooks'
            problem_graph = ', '.join([f'{a} -> {b}'
                                       for a, b in nx.find_cycle(dag)])
            raise Exception(f'{msg}: {problem_graph}')

        rv = []
        for hook_name in order:
            hook_tuple = dag.nodes[hook_name].get('hook_tuple')
            if hook_tuple:
                rv.append(hook_tuple)
        return rv
