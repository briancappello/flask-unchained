import importlib
import inspect
import os
import sys

from types import FunctionType, ModuleType
from typing import *

from py_meta_utils import Singleton

from .bundles import AppBundle, Bundle
from .constants import DEV, PROD, STAGING, TEST
from .exceptions import BundleNotFoundError
from .flask_unchained import FlaskUnchained
from .unchained import unchained
from .utils import cwd_import


def maybe_set_app_factory_from_env():
    app_factory = os.getenv('FLASK_APP_FACTORY', None)
    if app_factory:
        module_name, class_name = app_factory.rsplit('.', 1)
        app_factory_cls = getattr(cwd_import(module_name), class_name)
        AppFactory.set_singleton_class(app_factory_cls)


class AppFactory(metaclass=Singleton):
    """
    This class implements the `Application Factory Pattern`_ for Flask Unchained.

    .. _Application Factory Pattern: http://flask.pocoo.org/docs/1.0/patterns/appfactories/
    """

    APP_CLASS = FlaskUnchained
    """
    Set :attr:`APP_CLASS` to use a custom subclass of
    :class:`~flask_unchained.FlaskUnchained`.
    """

    REQUIRED_BUNDLES = [
        'flask_unchained.bundles.babel',
        'flask_unchained.bundles.controller',
    ]

    def create_app(self,
                   env: Union[DEV, PROD, STAGING, TEST],
                   bundles: Optional[List[str]] = None,
                   _config_overrides: Optional[Dict[str, Any]] = None,
                   **flask_kwargs,
                   ) -> FlaskUnchained:
        """
        Flask Unchained Application Factory. Returns an instance of
        :attr:`APP_CLASS` (by default, :class:`~flask_unchained.FlaskUnchained`).

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

    def create_basic_app(self,
                         bundles: List[Bundle] = None,
                         unchained_config: Optional[ModuleType] = None,
                         _config_overrides: Dict[str, Any] = None,
                         ) -> FlaskUnchained:
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
            name for i, (name, param)
            in enumerate(inspect.signature(self.APP_CLASS).parameters.items())
            if i > 0 and (
                    param.kind == param.POSITIONAL_OR_KEYWORD
                    or param.kind == param.KEYWORD_ONLY
            )
        }
        for kw in valid_flask_kwargs:
            if hasattr(unchained_config, kw.upper()):
                flask_kwargs.setdefault(kw, getattr(unchained_config, kw.upper()))
            elif kw in {'static_folder', 'template_folder'}:
                flask_kwargs.setdefault(kw, None)

        return self.APP_CLASS(app_import_name, **flask_kwargs)

    @staticmethod
    def load_unchained_config(env: Union[DEV, PROD, STAGING, TEST]) -> ModuleType:
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
            bundles.append(self.load_bundle(bundle_package_name))

        if not isinstance(bundles[-1], AppBundle):
            return None, bundles
        return bundles[-1], bundles

    def load_bundle(self,
                    bundle_package_name: str,
                    ) -> Union[AppBundle, Bundle]:
        for module_name in [f'{bundle_package_name}.bundle', bundle_package_name]:
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                if str(e) == f"No module named '{module_name}'":
                    continue
                raise e

            try:
                bundle_class = inspect.getmembers(module, self.is_bundle(module))[0][1]
            except IndexError:
                continue
            else:
                return bundle_class()

        raise BundleNotFoundError(
            f'Unable to find a Bundle subclass in the {bundle_package_name} bundle!'
            ' Please make sure this bundle is installed and that there is a Bundle'
            ' subclass in the packages\'s bundle module or its __init__.py file.')

    def is_bundle(self, module: ModuleType) -> FunctionType:
        def _is_bundle(obj):
            return (
                isinstance(obj, type) and issubclass(obj, Bundle)
                and obj not in {AppBundle, Bundle}
                and obj.__module__.startswith(module.__name__)
            )
        return _is_bundle


__all__ = [
    'AppFactory',
    'maybe_set_app_factory_from_env',
]
