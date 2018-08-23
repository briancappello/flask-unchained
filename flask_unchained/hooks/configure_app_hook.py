from flask import Config
from typing import *

from ..app_config import AppConfig
from ..app_factory_hook import AppFactoryHook
from ..bundle import Bundle, AppBundle
from ..constants import DEV, PROD, STAGING, TEST
from ..flask_unchained import FlaskUnchained
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
    Updates ``app.config`` with the settings from each bundle.
    """

    bundle_module_name = 'config'
    """
    By default, look for config classes in the ``config`` module of bundles.

    Override by setting the ``config_module_name`` attribute on your bundle class.
    """

    name = 'configure_app'
    run_after = ['extensions']

    def run_hook(self,
                 app: FlaskUnchained,
                 bundles: List[Bundle],
                 _config_overrides: Optional[Dict[str, Any]] = None,
                 ) -> None:
        """
        For each bundle in ``unchained_config.BUNDLES``, iterate through that
        bundle's class hierarchy, starting from the base-most bundle. For each
        bundle in that order, look for a ``config`` module, and if it exists,
        update ``app.config`` with the options first from a base ``Config`` class,
        if it exists, and then also if it exists, from an env-specific config class:
        one of ``DevConfig``, ``ProdConfig``, ``StagingConfig``, or ``TestConfig``.
        """
        self.apply_default_config(app)
        for bundle_ in bundles:
            for bundle in bundle_.iter_class_hierarchy():
                bundle_config = self.get_config(bundle, app.env)
                app.config.from_mapping(bundle_config)

        if _config_overrides and isinstance(_config_overrides, dict):
            app.config.from_mapping(_config_overrides)

    def apply_default_config(self, app: FlaskUnchained) -> None:
        from ..app_config import _ConfigDefaults
        app.config.from_object(_ConfigDefaults)

        if app.env == DEV:
            from ..app_config import _DevConfigDefaults
            app.config.from_object(_DevConfigDefaults)
        elif app.env == TEST:
            from ..app_config import _TestConfigDefaults
            app.config.from_object(_TestConfigDefaults)

    def get_config(self,
                   bundle: Bundle,
                   env: Union[DEV, PROD, STAGING, TEST],
                   ) -> AttrDict:
        bundle_config_module = self.import_bundle_module(bundle)
        base_config = getattr(bundle_config_module, BASE_CONFIG, None)
        env_config = getattr(bundle_config_module, ENV_CONFIGS[env], None)

        if (isinstance(bundle, AppBundle) and (
                not base_config
                or not issubclass(base_config, AppConfig))):
            raise Exception("Could not find an AppConfig subclass in your app "
                            "bundle's config module.")

        merged = Config(None)
        for config in [base_config, env_config]:
            if config:
                merged.from_object(config)

        if isinstance(bundle, AppBundle) and 'SECRET_KEY' not in merged:
            raise Exception("The `SECRET_KEY` config option is required. "
                            "Please set it in your app bundle's base `Config` class.")

        return AttrDict(merged)
