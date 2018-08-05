from flask import Flask, Config
from typing import *

from ..app_factory_hook import AppFactoryHook
from ..bundle import Bundle
from ..constants import DEV, PROD, STAGING, TEST
from ..utils import AttrDict

BASE_CONFIG = 'Config'
ENV_CONFIGS = {
    DEV: 'DevConfig',
    PROD: 'ProdConfig',
    STAGING: 'StagingConfig',
    TEST: 'TestConfig',
}


class ConfigureAppHook(AppFactoryHook):
    """
    Updates app.config with the default settings of each bundle.
    """
    bundle_module_name = 'config'
    name = 'configure_app'
    run_after = ['extensions']

    def run_hook(self,
                 app: Flask,
                 bundles: List[Type[Bundle]],
                 _config_overrides: Optional[Dict[str, Any]] = None,
                 ):
        self.apply_default_config(app)
        for bundle_ in bundles:
            for bundle in bundle_.iter_class_hierarchy():
                bundle_config = self.get_config(bundle, app.env)
                app.config.from_mapping(bundle_config)

        if _config_overrides and isinstance(_config_overrides, dict):
            app.config.from_mapping(_config_overrides)

    def apply_default_config(self, app):
        from ..app_config import _ConfigDefaults
        app.config.from_object(_ConfigDefaults)

        if app.env == DEV:
            from ..app_config import _DevConfigDefaults
            app.config.from_object(_DevConfigDefaults)
        elif app.env == TEST:
            from ..app_config import _TestConfigDefaults
            app.config.from_object(_TestConfigDefaults)

    def get_config(self, bundle: Type[Bundle],
                   env: Union[DEV, PROD, STAGING, TEST],
                   ) -> AttrDict:
        bundle_config_module = self.import_bundle_module(bundle)
        base_config = getattr(bundle_config_module, BASE_CONFIG, None)
        env_config = getattr(bundle_config_module, ENV_CONFIGS[env], None)

        merged = Config(None)
        for config in [base_config, env_config]:
            if config:
                merged.from_object(config)
        return AttrDict(merged)
