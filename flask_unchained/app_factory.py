import importlib
import inspect
import os
import sys

from typing import *

from .bundle import AppBundle, Bundle
from .constants import DEV, PROD, STAGING, TEST
from .exceptions import BundleNotFoundError
from .flask_unchained import FlaskUnchained
from .unchained import unchained


REQUIRED_BUNDLES = [
    'flask_unchained.bundles.babel',
    'flask_unchained.bundles.controller',
]


class AppFactory:
    @classmethod
    def create_app(cls,
                   env: Union[DEV, PROD, STAGING, TEST],
                   bundles: Optional[List[str]] = None,
                   **flask_kwargs,
                   ) -> FlaskUnchained:
        """
        Flask Unchained Application Factory

        :param env: Which environment the app should run in. Should be one of
            "development", "production", "staging", or "test" (you can import
            them: `from flask_unchained import DEV, PROD, STAGING, TEST`)
        :param bundles: An optional list of bundle modules names to use (mainly
            useful for testing)
        :param flask_kwargs: keyword argument overrides to the Flask constructor
        :return: the FlaskUnchained application instance
        """
        unchained_config = _load_unchained_config(env)
        bundles = bundles or getattr(unchained_config, 'BUNDLES', [])
        for b in REQUIRED_BUNDLES:
            if b not in bundles:
                bundles.insert(0, b)

        app_bundle, bundles = _load_bundles(bundles)
        if app_bundle is None and env != TEST:
            return cls.create_bundle_app(bundles)

        for k in ['TEMPLATE_FOLDER', 'STATIC_FOLDER', 'STATIC_URL_PATH']:
            flask_kwargs.setdefault(k.lower(), getattr(unchained_config, k, None))

        app_import_name = app_bundle and app_bundle.module_name or 'tests'
        app = FlaskUnchained(app_import_name, **flask_kwargs)

        # Flask assumes the root_path is based on the app_import_name, but
        # we want it to be the project root, not the app bundle root
        app.root_path = os.path.dirname(app.root_path)
        app.static_folder = flask_kwargs['static_folder']

        unchained.log_action('flask', {'app_name': app_import_name,
                                       'root_path': app.root_path,
                                       'kwargs': flask_kwargs})

        for bundle in bundles:
            bundle.before_init_app(app)

        unchained.init_app(app, env, bundles)

        for bundle in bundles:
            bundle.after_init_app(app)

        return app

    @classmethod
    def create_bundle_app(cls, bundles):
        """
        Creates an app for use while developing bundles
        """
        app = FlaskUnchained(bundles[-1].module_name, template_folder=os.path.join(
            os.path.dirname(__file__), 'templates'))

        for bundle in bundles:
            bundle.before_init_app(app)

        unchained.init_app(app, DEV, bundles)

        for bundle in bundles:
            bundle.after_init_app(app)

        return app


def _load_unchained_config(env: Union[DEV, PROD, STAGING, TEST]):
    if not sys.path or sys.path[0] != os.getcwd():
        sys.path.insert(0, os.getcwd())

    msg = None
    if env == TEST:
        try:
            return importlib.import_module('tests._unchained_config')
        except ImportError as e:
            msg = f'{e.msg}: Could not find _unchained_config.py in the tests directory'

    try:
        return importlib.import_module('unchained_config')
    except ImportError as e:
        if not msg:
            msg = f'{e.msg}: Could not find unchained_config.py in the project root'
        e.msg = msg
        raise e


def _load_bundles(bundle_package_names: List[str],
                  ) -> Tuple[Union[None, Type[AppBundle]], List[Type[Bundle]]]:
    if not bundle_package_names:
        return None, []

    bundles = []
    for bundle_package_name in bundle_package_names:
        bundle = _load_bundle(bundle_package_name, _is_bundle)
        bundles.append(bundle)
        unchained.log_action('bundle', bundle)

    if not issubclass(bundles[-1], AppBundle):
        return None, bundles
    return bundles[-1], bundles


def _load_bundle(bundle_package_name: str, type_checker):
    for module_name in [f'{bundle_package_name}.bundle', bundle_package_name]:
        try:
            module = importlib.import_module(module_name)
        except (ImportError, ModuleNotFoundError) as e:
            if bundle_package_name in str(e):
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


def _is_bundle(module):
    def is_bundle(obj):
        if not inspect.isclass(obj):
            return False
        is_subclass = issubclass(obj, Bundle) and obj not in {AppBundle, Bundle}
        return is_subclass and module.__name__ in obj.__module__
    return is_bundle
