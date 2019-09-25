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
        :param bundles: An optional list of bundle modules names to use. Overrides
                        ``unchained_config.BUNDLES`` (mainly useful for testing).
        :param flask_kwargs: keyword argument overrides for the :class:`FlaskUnchained`
                             constructor
        :param _config_overrides: a dictionary of config option overrides; meant for
                                  test fixtures.
        :return: The :class:`~flask_unchained.FlaskUnchained` application instance
        """
        unchained_config = self.load_unchained_config(env)
        app_bundle, bundles = self.load_bundles(
            bundle_package_names=bundles or getattr(unchained_config, 'BUNDLES', []),
            unchained_config=unchained_config,
        )

        if app_bundle is None and env != TEST:
            return self.create_basic_app(bundles, unchained_config, _config_overrides=_config_overrides)

        app = self.instantiate_app(app_bundle, unchained_config, **flask_kwargs)

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
        name = bundles[-1] if bundles else 'basic_app'
        app = self.instantiate_app(name, unchained_config, template_folder=os.path.join(
            os.path.dirname(__file__), 'templates'))

        for bundle in bundles:
            bundle.before_init_app(app)

        unchained.init_app(app, DEV, bundles, _config_overrides=_config_overrides)

        for bundle in bundles:
            bundle.after_init_app(app)

        return app

    def instantiate_app(self,
                        app_import_name_or_bundle: Union[str, Bundle, None],
                        unchained_config: ModuleType,
                        **flask_kwargs,
                        ) -> FlaskUnchained:
        bundle = (app_import_name_or_bundle
                  if isinstance(app_import_name_or_bundle, Bundle) else None)

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

        root_path = getattr(unchained_config, 'ROOT_PATH', None)
        if not root_path and bundle and bundle.is_single_module:
            root_path = bundle.root_path

        def root_folder_or_none(folder_name):
            if not root_path:
                return None
            folder = os.path.join(root_path, folder_name)
            return folder if os.path.isdir(folder) else None

        if 'template_folder' not in flask_kwargs:
            flask_kwargs.setdefault('template_folder', root_folder_or_none('templates'))

        if 'static_folder' not in flask_kwargs:
            flask_kwargs.setdefault('static_folder', root_folder_or_none('static'))

        if flask_kwargs['static_folder'] and not flask_kwargs.get('static_url_path', None):
            flask_kwargs['static_url_path'] = '/static'

        app_import_name = (bundle.module_name.split('.')[0] if bundle
                           else (app_import_name_or_bundle or 'tests'))
        app = self.APP_CLASS(app_import_name, **flask_kwargs)

        if not root_path and bundle and not bundle.is_single_module:
            # Flask assumes the root_path is based on the app_import_name, but
            # we want it to be the project root, not the app bundle root
            app.root_path = os.path.dirname(app.root_path)
            app.static_folder = flask_kwargs['static_folder']

        return app

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

        unchained_config_module_name = os.getenv('UNCHAINED_CONFIG', 'unchained_config')
        try:
            return cwd_import(unchained_config_module_name)
        except ImportError as e:
            if not msg:
                msg = f'{e.msg}: Could not find {unchained_config_module_name}.py ' \
                      f'in the current working directory (are you in the project root?)'
            e.msg = msg
            raise e

    @classmethod
    def load_bundles(cls,
                     bundle_package_names: Optional[List[str]] = None,
                     unchained_config: Optional[ModuleType] = None,
                     ) -> Tuple[Union[None, AppBundle], List[Bundle]]:
        bundle_package_names = bundle_package_names or []
        for b in cls.REQUIRED_BUNDLES:
            if b not in bundle_package_names:
                bundle_package_names.insert(0, b)

        if not bundle_package_names:
            return None, []

        bundles = []
        for bundle_package_name in bundle_package_names:
            bundles.append(cls.load_bundle(bundle_package_name))

        if not isinstance(bundles[-1], AppBundle):
            if unchained_config:
                single_module_app_bundle = cls._bundle_from_module(unchained_config)
                if single_module_app_bundle:
                    bundles.append(single_module_app_bundle)
                return single_module_app_bundle, bundles
            return None, bundles
        return bundles[-1], bundles

    @classmethod
    def load_bundle(cls, bundle_package_name: str) -> Union[AppBundle, Bundle]:
        for module_name in [f'{bundle_package_name}.bundle', bundle_package_name]:
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                if f"No module named '{module_name}'" in str(e):
                    continue
                raise e

            bundle = cls._bundle_from_module(module)
            if bundle:
                return bundle

        raise BundleNotFoundError(
            f'Unable to find a Bundle subclass in the {bundle_package_name} bundle!'
            ' Please make sure this bundle is installed and that there is a Bundle'
            ' subclass in the packages\'s bundle module or its __init__.py file.')

    @classmethod
    def is_bundle(cls, module: ModuleType) -> FunctionType:
        def _is_bundle(obj):
            return (
                isinstance(obj, type) and issubclass(obj, Bundle)
                and obj not in {AppBundle, Bundle}
                and obj.__module__.startswith(module.__name__)
            )
        return _is_bundle

    @classmethod
    def _bundle_from_module(cls, module: ModuleType) -> Union[AppBundle, Bundle, None]:
        try:
            bundle_class = inspect.getmembers(module, cls.is_bundle(module))[0][1]
        except IndexError:
            return None
        else:
            return bundle_class()


__all__ = [
    'AppFactory',
    'maybe_set_app_factory_from_env',
]
