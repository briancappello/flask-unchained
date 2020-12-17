import importlib
import inspect
import os
import sys

from types import ModuleType
from typing import *

from py_meta_utils import Singleton

from .bundles import AppBundle, Bundle
from .constants import DEV, PROD, STAGING, TEST, ENV_ALIASES, VALID_ENVS
from .exceptions import BundleNotFoundError
from .flask_unchained import FlaskUnchained
from .unchained import unchained
from .utils import cwd_import


def maybe_set_app_factory_from_env():
    app_factory = os.getenv('UNCHAINED_APP_FACTORY', None)
    if app_factory:
        module_name, class_name = app_factory.rsplit('.', 1)
        app_factory_cls = getattr(cwd_import(module_name), class_name)
        AppFactory.set_singleton_class(app_factory_cls)


class AppFactory(metaclass=Singleton):
    """
    The Application Factory Pattern for Flask Unchained.
    """

    APP_CLASS = FlaskUnchained
    """
    Set :attr:`APP_CLASS` to use a custom subclass of
    :class:`~flask_unchained.FlaskUnchained`.
    """

    REQUIRED_BUNDLES = [
        # these are ordered by first to be loaded
        'flask_unchained.bundles.controller',
        'flask_unchained.bundles.babel',  # requires controller bundle
    ]

    def create_app(self,
                   env: Union[DEV, PROD, STAGING, TEST],
                   bundles: Optional[List[str]] = None,
                   *,
                   _config_overrides: Optional[Dict[str, Any]] = None,
                   _load_unchained_config: bool = True,
                   **app_kwargs,
                   ) -> FlaskUnchained:
        """
        Flask Unchained Application Factory. Returns an instance of
        :attr:`APP_CLASS` (by default, :class:`~flask_unchained.FlaskUnchained`).

        Example Usage::

            app = AppFactory().create_app(PROD)

        :param env: Which environment the app should run in. Should be one of
                    "development", "production", "staging", or "test" (you can import
                    them: ``from flask_unchained import DEV, PROD, STAGING, TEST``)
        :type env: str
        :param bundles: An optional list of bundle modules names to use. Overrides
                        ``unchained_config.BUNDLES`` (mainly useful for testing).
        :type bundles: List[str]
        :param app_kwargs: keyword argument overrides for the :attr:`APP_CLASS`
                           constructor
        :type app_kwargs: Dict[str, Any]
        :param _config_overrides: a dictionary of config option overrides; meant for
                                  test fixtures (for internal use only).
        :param _load_unchained_config: Whether or not to try to load unchained_config
                                       (for internal use only).
        :return: The initialized :attr:`APP_CLASS` app instance, ready to rock'n'roll
        """
        env = ENV_ALIASES.get(env, env)
        if env not in VALID_ENVS:
            valid_envs = [f'{x!r}' for x in VALID_ENVS]
            raise ValueError(f"env must be one of {', '.join(valid_envs)}")

        unchained_config = {}
        unchained_config_module = None
        if _load_unchained_config:
            unchained_config_module = self.load_unchained_config(env)
            unchained_config = {k: v for k, v in vars(unchained_config_module).items()
                                if not k.startswith('_') and k.isupper()}
        unchained_config['_CONFIG_OVERRIDES'] = _config_overrides

        _, bundles = self.load_bundles(
            bundle_package_names=bundles or unchained_config.get('BUNDLES', []),
            unchained_config_module=unchained_config_module)

        app_import_name = (bundles[-1].module_name.split('.')[0] if bundles
                           else ('tests' if env == TEST else 'dev_app'))
        app = self.APP_CLASS(app_import_name, **self.get_app_kwargs(
            app_kwargs, bundles, env, unchained_config))
        app.env = env

        for bundle in bundles:
            bundle.before_init_app(app)

        unchained.init_app(app, bundles, unchained_config)

        for bundle in bundles:
            bundle.after_init_app(app)

        return app

    @staticmethod
    def load_unchained_config(env: Union[DEV, PROD, STAGING, TEST]) -> ModuleType:
        """
        Load the unchained config from the current working directory for the given
        environment. If ``env == "test"``, look for ``tests._unchained_config``,
        otherwise check the value of the ``UNCHAINED`` environment variable,
        falling back to loading the ``unchained_config`` module.
        """
        if not sys.path or sys.path[0] != os.getcwd():
            sys.path.insert(0, os.getcwd())

        msg = None
        if env == TEST:
            try:
                return cwd_import('tests._unchained_config')
            except ImportError as e:
                msg = f'{e.msg}: Could not find _unchained_config.py in the tests directory'

        unchained_config_module_name = os.getenv('UNCHAINED', 'unchained_config')
        try:
            return cwd_import(unchained_config_module_name)
        except ImportError as e:
            if not msg:
                msg = f'{e.msg}: Could not find {unchained_config_module_name}.py ' \
                      f'in the current working directory (are you in the project root?)'
            e.msg = msg
            raise e

    def get_app_kwargs(self,
                       app_kwargs: Dict[str, Any],
                       bundles: List[Bundle],
                       env: Union[DEV, PROD, STAGING, TEST],
                       unchained_config: Dict[str, Any],
                       ) -> Dict[str, Any]:
        """
        Returns ``app_kwargs`` with default settings applied from ``unchained_config``.
        """
        # this is for developing standalone bundles (as opposed to regular apps)
        if not isinstance(bundles[-1], AppBundle) and env != TEST:
            app_kwargs['template_folder'] = os.path.join(
                os.path.dirname(__file__), 'templates')

        # set kwargs to pass to Flask from the unchained_config
        params = inspect.signature(self.APP_CLASS).parameters
        valid_app_kwargs = [name for i, (name, param) in enumerate(params.items())
                            if i > 0 and (param.kind == param.POSITIONAL_OR_KEYWORD
                                          or param.kind == param.KEYWORD_ONLY)]
        for kw in valid_app_kwargs:
            config_key = kw.upper()
            if config_key in unchained_config:
                app_kwargs.setdefault(kw, unchained_config[config_key])

        # set up the root static/templates folders (if any)
        root_path = app_kwargs.get('root_path')
        if not root_path and bundles:
            root_path = bundles[-1].root_path
            if not bundles[-1].is_single_module:
                root_path = os.path.dirname(root_path)
            app_kwargs['root_path'] = root_path

        def root_folder_or_none(folder_name):
            if not root_path:
                return None
            folder = os.path.join(root_path, folder_name)
            return folder if os.path.isdir(folder) else None

        app_kwargs.setdefault('template_folder', root_folder_or_none('templates'))
        app_kwargs.setdefault('static_folder', root_folder_or_none('static'))
        if app_kwargs['static_folder'] and not app_kwargs.get('static_url_path'):
            app_kwargs.setdefault('static_url_path', '/static')

        return app_kwargs

    @classmethod
    def load_bundles(cls,
                     bundle_package_names: Optional[List[str]] = None,
                     unchained_config_module: Optional[ModuleType] = None,
                     ) -> Tuple[Union[None, AppBundle], List[Bundle]]:
        """
        Load bundle instances from the given list of bundle packages. If
        ``unchained_config_module`` is given and there was no app bundle listed
        in ``bundle_package_names``, attempt to load the app bundle from the
        unchained config.
        """
        bundle_package_names = bundle_package_names or []
        for bundle_name in reversed(cls.REQUIRED_BUNDLES):
            try:
                existing_index = bundle_package_names.index(bundle_name)
            except ValueError:
                pass
            else:
                bundle_package_names.pop(existing_index)
            bundle_package_names.insert(0, bundle_name)

        if not bundle_package_names:
            return None, []

        bundles = []
        for bundle_package_name in bundle_package_names:
            bundles.append(cls.load_bundle(bundle_package_name))

        if isinstance(bundles[-1], AppBundle):
            return bundles[-1], bundles

        if unchained_config_module:
            single_module_app_bundle = cls.bundle_from_module(unchained_config_module)
            if single_module_app_bundle:
                bundles.append(single_module_app_bundle)
            return single_module_app_bundle, bundles
        return None, bundles

    @classmethod
    def load_bundle(cls, bundle_package_name: str) -> Union[AppBundle, Bundle]:
        """
        Attempt to load the bundle instance from the given package.
        """
        for module_name in [f'{bundle_package_name}.bundle', bundle_package_name]:
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                if f"No module named '{module_name}'" in str(e):
                    continue
                raise e

            bundle = cls.bundle_from_module(module)
            if bundle:
                return bundle

        raise BundleNotFoundError(
            f'Unable to find a Bundle subclass in the {bundle_package_name} bundle!'
            ' Please make sure this bundle is installed and that there is a Bundle'
            ' subclass in the packages\'s __init__.py (or bundle.py) file.')

    @classmethod
    def bundle_from_module(cls, module: ModuleType) -> Union[AppBundle, Bundle, None]:
        """
        Attempt to instantiate the bundle class from the given module.
        """
        try:
            bundle_class = inspect.getmembers(module, cls._is_bundle(module))[0][1]
        except IndexError:
            return None
        else:
            return bundle_class()

    @classmethod
    def _is_bundle(cls, module: ModuleType) -> Callable[[Any], bool]:
        return lambda obj: (isinstance(obj, type) and issubclass(obj, Bundle)
                            and obj not in {AppBundle, Bundle}
                            and obj.__module__.startswith(module.__name__))


__all__ = [
    'AppFactory',
    'maybe_set_app_factory_from_env',
]
