import importlib
import inspect
import os
import sys

from flask import Flask
from flask.cli import prepare_exec_for_file
from typing import *

from .bundle import AppBundle, Bundle
from .constants import DEV, PROD, STAGING, TEST
from .hooks.configure_app_hook import ConfigureAppHook
from .unchained import unchained


class BundleNotFoundError(Exception):
    pass


class AppFactory:
    @classmethod
    def create_app(cls,
                   app_bundle_name: str,
                   env: Union[DEV, PROD, STAGING, TEST],
                   bundles: Optional[List[str]] = None,
                   **flask_kwargs,
                   ) -> Flask:
        app_bundle = _load_app_bundle(app_bundle_name)
        app_bundle_config = ConfigureAppHook(unchained).get_config(app_bundle,
                                                                   env)
        bundles = _load_bundles(bundles or app_bundle_config.BUNDLES)

        for k in ['TEMPLATE_FOLDER', 'STATIC_FOLDER', 'STATIC_URL_PATH']:
            flask_kwargs.setdefault(k.lower(), app_bundle_config.get(k))

        app = Flask(app_bundle.module_name, **flask_kwargs)

        unchained.log_action('flask', {'app_name': app_bundle.module_name,
                                       'kwargs': flask_kwargs})

        for bundle in bundles:
            bundle.before_init_app(app)

        unchained.init_app(app, env, bundles)

        for bundle in bundles:
            bundle.after_init_app(app)

        return app


def _load_bundles(bundle_package_names: List[str]) -> List[Type[Bundle]]:
    bundles = []
    for bundle_package_name in bundle_package_names:
        bundle = _load_bundle(bundle_package_name, _is_bundle)
        bundles.append(bundle)
        unchained.log_action('bundle', bundle)
    return bundles


def _load_app_bundle(app_bundle_name) -> Type[AppBundle]:
    if os.path.isfile(app_bundle_name):
        app_bundle_name = prepare_exec_for_file(app_bundle_name)
    else:
        sys.path.insert(0, os.getcwd())

    try:
        return _load_bundle(app_bundle_name, _is_app_bundle)
    except BundleNotFoundError:
        raise BundleNotFoundError(
            'Unable to locate your AppBundle. Please verify the Bundle subclass'
            f'in the `{app_bundle_name}` package subclasses '
            f'`flask_unchained.AppBundle`, and that `{app_bundle_name}` is '
            'the correct path.')


def _load_bundle(bundle_package_name: str, type_checker):
    for module_name in [f'{bundle_package_name}.bundle', bundle_package_name]:
        try:
            module = importlib.import_module(module_name)
        except (ImportError, ModuleNotFoundError) as e:
            if module_name in str(e):
                continue
            raise e

        try:
            return inspect.getmembers(module, type_checker(module))[0][1]
        except IndexError:
            continue

    raise BundleNotFoundError(
        f'Unable to find a Bundle subclass in the {bundle_package_name} bundle!'
        ' Please make sure this bundle is installed and that there is a Bundle'
        ' subclass in the packages\'s bundle module or its __init__.py file.')


def _is_app_bundle(module):
    def is_app_bundle(obj):
        return _is_bundle(module)(obj) and issubclass(obj, AppBundle)
    return is_app_bundle


def _is_bundle(module):
    def is_bundle(obj):
        if not inspect.isclass(obj):
            return False
        is_subclass = issubclass(obj, Bundle) and obj not in {AppBundle, Bundle}
        return is_subclass and module.__name__ in obj.__module__
    return is_bundle
