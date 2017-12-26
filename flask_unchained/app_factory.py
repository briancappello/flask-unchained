import inspect

from datetime import datetime
from typing import List

from flask import Flask

from .base_config import AppConfig
from .bundle import Bundle
from .unchained_extension import UnchainedExtension
from .utils import safe_import_module


class AppFactory:
    _unchained = UnchainedExtension()

    @classmethod
    def create_app(cls, app_config_cls: AppConfig, **flask_kwargs):
        bundles = _load_bundles(app_config_cls)
        app_name = bundles[-1].name
        for k, v in getattr(app_config_cls, 'FLASK_KWARGS', {}).items():
            flask_kwargs.setdefault(k, v)

        timestamp = datetime.now()
        app = Flask(app_name, **flask_kwargs)

        unchained = cls._unchained.init_app(app, app_config_cls, bundles)
        unchained.register_action_table('flask',
                                        ['app_name', 'kwargs'],
                                        lambda d: [d['app_name'], d['kwargs']])
        unchained.log_action('flask',
                             {'app_name': app_name, 'kwargs': flask_kwargs},
                             timestamp)
        return app


def _load_bundles(app_config_cls: AppConfig) -> List[Bundle]:
    loaded_bundles = set()
    bundles = []
    for bundle_module_name in app_config_cls.BUNDLES:
        module = safe_import_module(bundle_module_name)
        bundle_found = False
        for name, bundle in inspect.getmembers(module, _is_bundle_cls):
            # FIXME test overriding bundles works as expected
            if bundle.name not in loaded_bundles:  # avoid getting superclasses
                bundles.append(bundle)
                loaded_bundles.add(bundle.name)
                bundle_found = True
                break

        if not bundle_found:
            raise Exception(
                f'Unable to find a Bundle subclass for the '
                f'{bundle_module_name} bundle! Please make sure it\'s '
                f'installed and that there is a Bundle subclass in (or '
                f'imported in) the module\'s __init__.py file.')
    return bundles


def _is_bundle_cls(obj) -> bool:
    if not inspect.isclass(obj):
        return False
    return issubclass(obj, Bundle) and obj != Bundle
