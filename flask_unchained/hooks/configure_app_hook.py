from flask import Flask

from ..app_factory_hook import AppFactoryHook


class ConfigureAppHook(AppFactoryHook):
    """
    Updates app.config with the default settings of each bundle.
    """
    bundle_module_name = 'bundle_config'
    name = 'configure_app'
    priority = 5

    def run_hook(self, app: Flask, bundles):
        config_name = self.unchained.app_config_cls.__name__
        for bundle in bundles:
            bundle_config_module = self.import_bundle_module(bundle)
            bundle_config = getattr(bundle_config_module, config_name, None)
            if bundle_config:
                app.config.from_object(bundle_config)
        app.config.from_object(self.unchained.app_config_cls)

    def get_module_name(self, bundle):
        if bundle.app_bundle:
            return f'{bundle.module_name}.config'
        return super().get_module_name(bundle)
