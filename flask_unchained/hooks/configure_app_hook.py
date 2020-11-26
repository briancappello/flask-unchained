import flask

from typing import *

from ..config import BundleConfig
from ..app_factory_hook import AppFactoryHook
from ..bundles import Bundle, AppBundle
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

    name = 'configure_app'
    """
    The name of this hook.
    """

    bundle_module_name = 'config'
    """
    The default module this hook loads from.

    Override by setting the ``config_module_name`` attribute on your bundle class.
    """

    require_exactly_one_bundle_module = True
    run_after = ['register_extensions']

    def run_hook(self,
                 app: FlaskUnchained,
                 bundles: List[Bundle],
                 unchained_config: Optional[Dict[str, Any]] = None,
                 ) -> None:
        """
        For each bundle in ``unchained_config.BUNDLES``, iterate through that
        bundle's class hierarchy, starting from the base-most bundle. For each
        bundle in that order, look for a ``config`` module, and if it exists,
        update ``app.config`` with the options first from a base ``Config`` class,
        if it exists, and then also if it exists, from an env-specific config class:
        one of ``DevConfig``, ``ProdConfig``, ``StagingConfig``, or ``TestConfig``.
        """
        BundleConfig._set_current_app(app)

        self.apply_default_config(app, bundles and bundles[-1] or None)
        for bundle in bundles:
            app.config.from_mapping(self.get_bundle_config(bundle, app.env))

        _config_overrides = (unchained_config.get('_CONFIG_OVERRIDES')
                             if unchained_config else None)
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
        """
        Get the config settings from a bundle hierarchy.
        """
        if isinstance(bundle, AppBundle):
            return self._get_bundle_config(bundle, env)

        config = flask.Config('.')
        for bundle_ in bundle._iter_class_hierarchy():
            config.update(self._get_bundle_config(bundle_, env))
        return config

    def _get_bundle_config(self,
                           bundle: Union[AppBundle, Bundle],
                           env: Union[DEV, PROD, STAGING, TEST],
                           ) -> flask.Config:
        """
        Get the config settings from a single bundle package.
        """
        config = flask.Config('.')
        try:
            bundle_config_module = self.import_bundle_modules(bundle)[0]
        except IndexError:
            return config

        base_config = getattr(bundle_config_module, BASE_CONFIG_CLASS, None)
        env_config = getattr(bundle_config_module, ENV_CONFIG_CLASSES[env], None)
        for config_cls in [base_config, env_config]:
            if config_cls:
                config.from_object(config_cls)
        return config
