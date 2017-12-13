from flask import Flask

from ..factory_hook import FactoryHook


class ConfigureAppHook(FactoryHook):
    priority = 5
    bundle_module_name = 'bundle_config'

    def run_hook(self, app: Flask, app_config_cls, bundles):
        for bundle in bundles:
            bundle_config_module = self.import_bundle_module(bundle)
            bundle_config = getattr(
                bundle_config_module, app_config_cls.__name__, None)
            if bundle_config:
                app.config.from_object(bundle_config)

        app.config.from_object(app_config_cls)
