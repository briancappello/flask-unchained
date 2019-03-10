import flask

from typing import *

from ..config import AppBundleConfig, BundleConfig
from ..app_factory_hook import AppFactoryHook
from ..bundle import Bundle, AppBundle
from ..constants import DEV, PROD, STAGING, TEST
from ..flask_unchained import FlaskUnchained


BASE_CONFIG_CLASS = 'Config'

ENV_CONFIG_CLASSES = {
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
        self.apply_default_config(app, bundles and bundles[-1] or None)
        BundleConfig._set_current_app(app)
        for bundle_ in bundles:
            for bundle in bundle_._iter_class_hierarchy():
                app.config.from_mapping(self.get_bundle_config(bundle, app.env))

        if _config_overrides and isinstance(_config_overrides, dict):
            app.config.from_mapping(_config_overrides)

    def apply_default_config(self,
                             app: FlaskUnchained,
                             app_bundle: Optional[Bundle] = None,
                             ) -> None:
        from .. import config

        app.config.from_object(config._ConfigDefaults)
        if app.env == DEV:
            app.config.from_object(config._DevConfigDefaults)
        elif app.env == TEST:
            app.config.from_object(config._TestConfigDefaults)

        if isinstance(app_bundle, AppBundle):
            app_bundle_config = self.get_bundle_config(app_bundle, app.env)
            app.config.from_mapping(app_bundle_config)

    def get_bundle_config(self,
                          bundle: Bundle,
                          env: Union[DEV, PROD, STAGING, TEST],
                          ) -> flask.Config:
        bundle_config_module = self.import_bundle_module(bundle)
        base_config = getattr(bundle_config_module, BASE_CONFIG_CLASS, None)
        env_config = getattr(bundle_config_module, ENV_CONFIG_CLASSES[env], None)

        if isinstance(bundle, AppBundle):
            if not bundle_config_module:
                module_name = self.get_bundle_module_name(bundle)
                raise Exception(
                    f'Could not find the `{module_name}` module in your app bundle.')

            if not base_config or not issubclass(base_config, AppBundleConfig):
                raise Exception(
                    f"Could not find an AppBundleConfig subclass named "
                    f"{BASE_CONFIG_CLASS} in your app bundle's "
                    f"{self.get_module_name(bundle)} module.")

        merged = flask.Config(None)
        for config in [base_config, env_config]:
            if config:
                merged.from_object(config)

        if isinstance(bundle, AppBundle) and 'SECRET_KEY' not in merged:
            raise Exception(f"The `SECRET_KEY` config option is required. Please "
                            f"set it in your app bundle's {BASE_CONFIG_CLASS} class.")

        return merged
