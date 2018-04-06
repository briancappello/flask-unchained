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

    def run_hook(self, app: Flask, bundles: List[Type[Bundle]]):
        env = self.unchained.env
        for bundle_ in bundles:
            for bundle in bundle_.iter_bundles():
                bundle_config = self.get_config(bundle, env)
                app.config.from_mapping(bundle_config)

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
