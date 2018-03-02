import importlib
import inspect
import os
import sys

from flask import Flask
from flask.cli import prepare_exec_for_file
from typing import *

from .bundle import AppBundle, Bundle
from .constants import DEV, PROD, STAGING, TEST
from .unchained import unchained
from .utils import safe_import_module


class AppFactory:
    @classmethod
    def create_app(cls,
                   app_bundle_name: str,
                   env: Union[DEV, PROD, STAGING, TEST],
                   **flask_kwargs,
                   ) -> Flask:
        app_bundle, bundles = _load_bundles(app_bundle_name, env)
        app_config_cls = app_bundle.get_config(env)

        for k in ['TEMPLATE_FOLDER', 'STATIC_FOLDER', 'STATIC_URL_PATH']:
            flask_kwargs.setdefault(k.lower(), getattr(app_config_cls, k, None))

        app = Flask(app_bundle.module_name, **flask_kwargs)

        unchained.log_action('flask', {'app_name': app_bundle.module_name,
                                       'kwargs': flask_kwargs})

        for bundle in bundles:
            bundle.before_init_app(app)

        unchained.init_app(app, app_config_cls, bundles)

        for bundle in bundles:
            bundle.after_init_app(app)

        return app


def _load_bundles(app_bundle_name: str,
                  env: Union[DEV, PROD, STAGING, TEST],
                  ) -> Tuple[Type[AppBundle], List[Type[Bundle]]]:
    app_bundle = _load_app_bundle(app_bundle_name)

    bundles = []
    for bundle_module_name in app_bundle.get_config(env).BUNDLES:
        module = safe_import_module(bundle_module_name)
        bundle_found = False
        for name, bundle in inspect.getmembers(module, _is_bundle):
            # skip superclasses
            if bundle.__subclasses__():
                continue

            bundles.append(bundle)
            unchained.log_action('bundle', bundle)
            bundle_found = True

        if not bundle_found:
            raise Exception(
                f'Unable to find a Bundle subclass for the '
                f'{bundle_module_name} bundle! Please make sure it\'s '
                f'installed and that there is a Bundle subclass in (or '
                f'imported in) the module\'s __init__.py file.')

    bundles.append(app_bundle)
    return app_bundle, bundles


def _load_app_bundle(app_bundle_name) -> Type[AppBundle]:
    if os.path.isfile(app_bundle_name):
        app_bundle_name = prepare_exec_for_file(app_bundle_name)
    else:
        sys.path.insert(0, os.getcwd())

    app_module = importlib.import_module(app_bundle_name)
    for _, bundle in inspect.getmembers(app_module, _is_app_bundle):
        return bundle


def _is_app_bundle(obj) -> bool:
    if not inspect.isclass(obj):
        return False
    return issubclass(obj, AppBundle) and obj != AppBundle


def _is_bundle(obj) -> bool:
    if not inspect.isclass(obj) or issubclass(obj, AppBundle):
        return False
    return issubclass(obj, Bundle) and obj != Bundle
