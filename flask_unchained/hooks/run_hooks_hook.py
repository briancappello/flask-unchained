import inspect

from flask import Flask
from importlib import import_module
from typing import *

from ..app_factory_hook import AppFactoryHook
from ..bundle import Bundle


class RunHooksHook(AppFactoryHook):
    """
    An internal hook to discover and run all the other hooks
    """
    bundle_module_name = 'hooks'

    def run_hook(self, app: Flask, bundles: List[Type[Bundle]]):
        for hook in self.collect_from_bundles(bundles):
            if hook.action_category and hook.action_table_columns:
                self.unchained.register_action_table(hook.action_category,
                                                     hook.action_table_columns,
                                                     hook.action_table_converter)
            hook.run_hook(app, bundles)
            hook.update_shell_context(self.unchained._shell_ctx)
            self.unchained.log_action('hook', hook)

        app.shell_context_processor(lambda: self.unchained._shell_ctx)

    def collect_from_bundles(self, bundles: List[Type[Bundle]],
                             ) -> List[AppFactoryHook]:
        unchained_hooks = self._collect_from_package(
            import_module('flask_unchained.hooks'))
        hooks = [Hook(self.unchained) for _, Hook in unchained_hooks.items()]
        for bundle in bundles:
            hooks += self.collect_from_bundle(bundle)
        return sorted(hooks, key=lambda hook: hook.priority)

    def collect_from_bundle(self, bundle: Type[Bundle]) -> List[AppFactoryHook]:
        bundle_store = self.find_bundle_store(bundle)
        if bundle_store:
            bundle_store = bundle_store()
            self.unchained._bundle_stores[bundle.name] = bundle_store
        return [Hook(self.unchained, bundle_store) for _, Hook in
                super().collect_from_bundle(bundle).items()]

    def find_bundle_store(self, bundle):
        for bundle in bundle.iter_bundles():
            module = self.import_bundle_module(bundle)
            if hasattr(module, 'Store'):
                return module.Store

    def type_check(self, obj):
        is_class = inspect.isclass(obj) and issubclass(obj, AppFactoryHook)
        return is_class and obj not in {AppFactoryHook, RunHooksHook}
