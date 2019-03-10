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
    """
    This class implements the `Application Factory Pattern`_ for Flask Unchained.

    .. _Application Factory Pattern: http://flask.pocoo.org/docs/1.0/patterns/appfactories/
    """

    @classmethod
    def create_app(cls,
                   env: Union[DEV, PROD, STAGING, TEST],
                   bundles: Optional[List[str]] = None,
                   _config_overrides: Optional[Dict[str, Any]] = None,
                   **flask_kwargs) -> FlaskUnchained:
        """
        Flask Unchained Application Factory. Returns an instance of
        :class:`~flask_unchained.FlaskUnchained`.

        Example Usage::

            app = AppFactory.create_app(DEV)

        :param env: Which environment the app should run in. Should be one of
                    "development", "production", "staging", or "test" (you can import
                    them: ``from flask_unchained import DEV, PROD, STAGING, TEST``)
        :param bundles: An optional list of bundle modules names to use (mainly
                        useful for testing)
        :param flask_kwargs: keyword argument overrides for the :class:`FlaskUnchained`
                             constructor
        :param _config_overrides: a dictionary of config option overrides; meant for
                                  test fixtures.
        :return: The :class:`~flask_unchained.FlaskUnchained` application instance
        """
        unchained_config = _load_unchained_config(env)
        app_bundle, bundles = _load_bundles(
            bundles or getattr(unchained_config, 'BUNDLES', []))

        if app_bundle is None and env != TEST:
            return cls.create_basic_app(bundles, _config_overrides=_config_overrides)

        for k in ['TEMPLATE_FOLDER', 'STATIC_FOLDER', 'STATIC_URL_PATH']:
            flask_kwargs.setdefault(k.lower(), getattr(unchained_config, k, None))

        app_import_name = (app_bundle.module_name.split('.')[0]
                           if app_bundle else 'tests')
        app = FlaskUnchained(app_import_name, **flask_kwargs)

        # Flask assumes the root_path is based on the app_import_name, but
        # we want it to be the project root, not the app bundle root
        app.root_path = os.path.dirname(app.root_path)
        app.static_folder = flask_kwargs['static_folder']

        for bundle in bundles:
            bundle.before_init_app(app)

        unchained.init_app(app, env, bundles, _config_overrides=_config_overrides)

        for bundle in bundles:
            bundle.after_init_app(app)

        return app

    @classmethod
    def create_basic_app(cls, bundles=None, _config_overrides=None):
        """
        Creates a "fake" app for use while developing
        """
        bundles = bundles or []
        name = bundles[-1].module_name if bundles else 'basic_app'
        app = FlaskUnchained(name, template_folder=os.path.join(
            os.path.dirname(__file__), 'templates'))

        for bundle in bundles:
            bundle.before_init_app(app)

        unchained.init_app(app, DEV, bundles, _config_overrides=_config_overrides)

        for bundle in bundles:
            bundle.after_init_app(app)

        return app


def _cwd_import(module_name):
    module = importlib.import_module(module_name)
    expected_path = os.path.join(os.getcwd(), module_name.replace('.', os.sep) + '.py')
    if module.__file__ != expected_path:
        raise ImportError
    return module


def _load_unchained_config(env: Union[DEV, PROD, STAGING, TEST]):
    if not sys.path or sys.path[0] != os.getcwd():
        sys.path.insert(0, os.getcwd())

    msg = None
    if env == TEST:
        try:
            return _cwd_import('tests._unchained_config')
        except ImportError as e:
            msg = f'{e.msg}: Could not find _unchained_config.py in the tests directory'

    try:
        return _cwd_import('unchained_config')
    except ImportError as e:
        if not msg:
            msg = f'{e.msg}: Could not find unchained_config.py in the project root'
        e.msg = msg
        raise e


def _load_bundles(bundle_package_names: Optional[List[str]] = None,
                  ) -> Tuple[Union[None, AppBundle], List[Bundle]]:
    bundle_package_names = bundle_package_names or []
    for b in REQUIRED_BUNDLES:
        if b not in bundle_package_names:
            bundle_package_names.insert(0, b)

    if not bundle_package_names:
        return None, []

    bundles = []
    for bundle_package_name in bundle_package_names:
        bundle = _load_bundle(bundle_package_name, _is_bundle)
        bundles.append(bundle())

    if not isinstance(bundles[-1], AppBundle):
        return None, bundles
    return bundles[-1], bundles


def _load_bundle(bundle_package_name: str, type_checker):
    for module_name in [f'{bundle_package_name}.bundle', bundle_package_name]:
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            if str(e) == f"No module named '{module_name}'":
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
        if not isinstance(obj, type):
            return False
        is_subclass = issubclass(obj, Bundle) and obj not in {AppBundle, Bundle}
        return is_subclass and obj.__module__.startswith(module.__name__)
    return is_bundle


__all__ = [
    'AppFactory',
]
