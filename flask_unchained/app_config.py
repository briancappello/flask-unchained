import os
import sys

from py_meta_utils import OptionalClass

from .utils import get_boolean_env


class _CurrentAppMetaclass(type):
    current_app = OptionalClass()

    def _set_current_app(cls, app):
        cls.current_app = app


class BundleConfig(metaclass=_CurrentAppMetaclass):
    """
    Base class for bundle configs. Allows access to the app-under-construction
    as it's currently configured from the order bundles were declared in
    ``unchained_config.BUNDLES``. Example usage::

        # your_bundle_root/config.py

        import os

        from flask_unchained import BundleConfig

        class Config(BundleConfig):
            SHOULD_PRETTY_PRINT_JSON = BundleConfig.current_app.config.DEBUG
    """


class _AppRootDescriptor:
    def __get__(self, instance, cls):
        return os.path.dirname(sys.modules[cls.__module__].__file__)


class _ProjectRootDescriptor:
    def __get__(self, instance, cls):
        return os.path.abspath(os.path.join(cls.APP_ROOT, os.pardir))


class AppBundleConfig(BundleConfig):
    """
    Base class for app-bundle configs. Example usage::

        # project-root/your_app_bundle/config.py

        import os

        from flask_unchained import AppBundleConfig

        class Config(AppBundleConfig):
            SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'change-me-to-a-secret-key')

        class DevConfig(Config):
            pass

        class ProdConfig(Config):
            pass

        class StagingConfig(ProdConfig):
            pass

        class TestConfig(Config):
            pass
    """

    APP_ROOT: str = _AppRootDescriptor()
    """
    Root path of the app bundle. Determined automatically.
    """

    PROJECT_ROOT: str = _ProjectRootDescriptor()
    """
    Root path of the project. Determined automatically.
    """


class _ConfigDefaults:
    DEBUG = get_boolean_env('FLASK_DEBUG', False)


class _DevConfigDefaults:
    DEBUG = get_boolean_env('FLASK_DEBUG', True)


class _TestConfigDefaults:
    TESTING = True
    """
    Tell Flask we're in testing mode.
    """

    WTF_CSRF_ENABLED = False
    """
    Disable CSRF tokens in tests.
    """


__all__ = [
    'AppBundleConfig',
    'BundleConfig',
]
