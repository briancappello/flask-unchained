import importlib
import inspect
import os
import sys

from typing import *

from py_meta_utils import Singleton

from .bundles import AppBundle, Bundle
from .constants import DEV, PROD, STAGING, TEST
from .exceptions import BundleNotFoundError
from .flask_unchained import FlaskUnchained
from .unchained import unchained
from .utils import cwd_import


class AppFactory(metaclass=Singleton):
    """
    This class implements the `Application Factory Pattern`_ for Flask Unchained.

    .. _Application Factory Pattern: http://flask.pocoo.org/docs/1.0/patterns/appfactories/
    """

    FLASK_APP_CLASS = FlaskUnchained

    REQUIRED_BUNDLES = [
        'flask_unchained.bundles.babel',
        'flask_unchained.bundles.controller',
    ]

    def create_app(self,
                   env: Union[DEV, PROD, STAGING, TEST],
                   bundles: Optional[List[str]] = None,
                   _config_overrides: Optional[Dict[str, Any]] = None,
                   **flask_kwargs) -> FlaskUnchained:
        """
        Flask Unchained Application Factory. Returns an instance of
        :attr:`FLASK_APP_CLASS` (by default, :class:`~flask_unchained.FlaskUnchained`).

        Example Usage::

            app = AppFactory().create_app(PROD)

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
        unchained_config = self.load_unchained_config(env)
        app_bundle, bundles = self.load_bundles(
            bundles or getattr(unchained_config, 'BUNDLES', []))

        if app_bundle is None and env != TEST:
            return self.create_basic_app(bundles, unchained_config, _config_overrides=_config_overrides)

        app_import_name = (app_bundle.module_name.split('.')[0]
                           if app_bundle else 'tests')
        app = self.instantiate_app(app_import_name, unchained_config, **flask_kwargs)

        for bundle in bundles:
            bundle.before_init_app(app)

        unchained.init_app(app, env, bundles, _config_overrides=_config_overrides)

        for bundle in bundles:
            bundle.after_init_app(app)

        return app

    def create_basic_app(self, bundles=None, unchained_config=None, _config_overrides=None):
        """
        Creates a "fake" app for use while developing
        """
        bundles = bundles or []
        name = bundles[-1].module_name if bundles else 'basic_app'
        app = self.instantiate_app(name, unchained_config, template_folder=os.path.join(
            os.path.dirname(__file__), 'templates'))

        for bundle in bundles:
            bundle.before_init_app(app)

        unchained.init_app(app, DEV, bundles, _config_overrides=_config_overrides)

        for bundle in bundles:
            bundle.after_init_app(app)

        return app

    def instantiate_app(self,
                        app_import_name: str,
                        unchained_config: ModuleType,
                        **flask_kwargs,
                        ) -> FlaskUnchained:
        valid_flask_kwargs = {
            name for name, param
            in inspect.signature(self.FLASK_APP_CLASS).parameters.items()
            if name != 'import_name' and (
                    param.kind == param.POSITIONAL_OR_KEYWORD
                    or param.kind == param.KEYWORD_ONLY
            )
        }
        for k in valid_flask_kwargs:
            if hasattr(unchained_config, k.upper()):
                flask_kwargs.setdefault(k, getattr(unchained_config, k.upper()))

        return self.FLASK_APP_CLASS(app_import_name, **flask_kwargs)

    @staticmethod
    def load_unchained_config(env: Union[DEV, PROD, STAGING, TEST]):
        if not sys.path or sys.path[0] != os.getcwd():
            sys.path.insert(0, os.getcwd())

        msg = None
        if env == TEST:
            try:
                return cwd_import('tests._unchained_config')
            except ImportError as e:
                msg = f'{e.msg}: Could not find _unchained_config.py in the tests directory'

        try:
            return cwd_import('unchained_config')
        except ImportError as e:
            if not msg:
                msg = f'{e.msg}: Could not find unchained_config.py in the project root'
            e.msg = msg
            raise e

    def load_bundles(self,
                     bundle_package_names: Optional[List[str]] = None,
                     ) -> Tuple[Union[None, AppBundle], List[Bundle]]:
        bundle_package_names = bundle_package_names or []
        for b in self.REQUIRED_BUNDLES:
            if b not in bundle_package_names:
                bundle_package_names.insert(0, b)

        if not bundle_package_names:
            return None, []

        bundles = []
        for bundle_package_name in bundle_package_names:
            bundle = self.load_bundle(bundle_package_name, self.is_bundle)
            bundles.append(bundle())

        if not isinstance(bundles[-1], AppBundle):
            return None, bundles
        return bundles[-1], bundles

    def load_bundle(self, bundle_package_name: str, type_checker):
        type_checker = type_checker or self.is_bundle
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

    def is_bundle(self, module):
        def _is_bundle(obj):
            if not isinstance(obj, type):
                return False
            is_subclass = issubclass(obj, Bundle) and obj not in {AppBundle, Bundle}
            return is_subclass and obj.__module__.startswith(module.__name__)
        return _is_bundle


__all__ = [
    'AppFactory',
]
