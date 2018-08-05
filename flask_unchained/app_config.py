"""
    AppConfig
    ^^^^^^^^^

    Base class for app-bundle configs. Example usage::

        # file: project_root/your_app_bundle/config.py
        from flask_unchained import AppConfig

        class Config(AppConfig):
            pass

        class DevConfig(Config):
            pass

        class ProdConfig(Config):
            pass

        class StagingConfig(ProdConfig):
            pass

        class TestConfig(Config):
            pass
"""
import os
import sys


class AppRootDescriptor:
    def __get__(self, instance, cls):
        return os.path.dirname(sys.modules[cls.__module__].__file__)


class ProjectRootDescriptor:
    def __get__(self, instance, cls):
        return os.path.abspath(os.path.join(cls.APP_ROOT, os.pardir))


class AppConfig:
    """
    Base class for app-bundle configs.
    """

    APP_ROOT: str = AppRootDescriptor()
    """
    Root path of the app bundle. Determined automatically.
    """

    PROJECT_ROOT: str = ProjectRootDescriptor()
    """
    Root path of the project. Determined automatically.
    """



