import os
import sys

from .utils import get_boolean_env


class AppRootDescriptor:
    def __get__(self, instance, cls):
        return os.path.dirname(sys.modules[cls.__module__].__file__)


class ProjectRootDescriptor:
    def __get__(self, instance, cls):
        return os.path.abspath(os.path.join(cls.APP_ROOT, os.pardir))


class AppConfig:
    """
    Base class for app-bundle configs. Example usage::

        # project-root/your_app_bundle/config.py

        import os

        from flask_unchained import AppConfig

        class Config(AppConfig):
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

    APP_ROOT: str = AppRootDescriptor()
    """
    Root path of the app bundle. Determined automatically.
    """

    PROJECT_ROOT: str = ProjectRootDescriptor()
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
