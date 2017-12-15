from werkzeug.routing import UnicodeConverter

from ..app_factory_hook import AppFactoryHook
from ..base_config import FlaskUnchainedConfig as AppConfig
from ..flask_unchained import FlaskUnchained


class ConfigureAppHook(AppFactoryHook):
    priority = 5
    bundle_module_name = 'bundle_config'

    def run_hook(self, app: FlaskUnchained, app_config_cls: AppConfig, bundles):
        for bundle in bundles:
            bundle_config_module = self.import_bundle_module(bundle)
            bundle_config = getattr(
                bundle_config_module, app_config_cls.__name__, None)
            if bundle_config:
                app.config.from_object(bundle_config)
        app.config.from_object(app_config_cls)

        # the UnicodeConverter is the default, and it's registered with the
        # explicit name of "string", but since all the other converters use
        # the builtin python type names, we alias it to "str" for dev sanity
        app.url_map.converters['str'] = UnicodeConverter
