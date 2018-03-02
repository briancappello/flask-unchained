from flask import Flask
from typing import *

from ..app_factory_hook import AppFactoryHook
from ..bundle import AppBundle, Bundle


class ConfigureAppHook(AppFactoryHook):
    """
    Updates app.config with the default settings of each bundle.
    """
    bundle_module_name = 'bundle_config'
    name = 'configure_app'
    priority = 5

    def run_hook(self, app: Flask, bundles: List[Bundle]):
        config_name = self.unchained.app_config_cls.__name__
        for bundle_ in bundles:
            for bundle in bundle_.iter_bundles():
                bundle_config_module = self.import_bundle_module(bundle)
                base_config = getattr(bundle_config_module, 'BaseConfig', None)
                env_config = getattr(bundle_config_module, config_name, None)
                for config in [base_config, env_config]:
                    if config:
                        app.config.from_object(config)
        app.config.from_object(self.unchained.app_config_cls)

    def get_module_name(self, bundle: Type[Bundle]):
        if issubclass(bundle, AppBundle):
            return f'{bundle.module_name}.config'
        return super().get_module_name(bundle)
