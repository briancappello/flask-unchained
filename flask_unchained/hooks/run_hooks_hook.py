import inspect

from flask import Flask
from importlib import import_module
from typing import List

from ..app_factory_hook import AppFactoryHook
from ..bundle import Bundle


class RunHooksHook(AppFactoryHook):
    bundle_module_name = 'hooks'

    def run_hook(self, app: Flask, bundles: List[Bundle]):
        for hook in self.load_hooks(bundles):
            if hook.action_category and hook.action_table_columns:
                self.unchained.register_action_table(hook.action_category,
                                                     hook.action_table_columns,
                                                     hook.action_table_converter)
            hook.run_hook(app, bundles)
            hook.update_shell_context(self.unchained._shell_ctx)
            self.unchained.log_action('hook', hook)

        app.shell_context_processor(lambda: self.unchained._shell_ctx)

    def load_hooks(self, bundles: List[Bundle]) -> List[AppFactoryHook]:
        unchained_hooks = inspect.getmembers(
            import_module('flask_unchained.hooks'), self.type_check)
        hooks = [hook(self.unchained) for _, hook in unchained_hooks]
        for bundle in bundles:
            hooks += self.collect_from_bundle(bundle)
        return sorted(hooks, key=lambda hook: hook.priority)

    def collect_from_bundle(self, bundle: Bundle) -> List[AppFactoryHook]:
        bundle_store = getattr(self.import_bundle_module(bundle), 'Store', None)
        if bundle_store:
            bundle_store = bundle_store()
            self.unchained._bundle_stores[bundle.name] = bundle_store
        return [hook(self.unchained, bundle_store)
                for _, hook in super().collect_from_bundle(bundle)]

    def type_check(self, obj):
        is_class = inspect.isclass(obj) and issubclass(obj, AppFactoryHook)
        return is_class and obj not in {AppFactoryHook, RunHooksHook}
