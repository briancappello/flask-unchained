import os
import sys


class AppRootDescriptor:
    def __get__(self, instance, cls):
        return os.path.dirname(sys.modules[cls.__module__].__file__)


class ProjectRootDescriptor:
    def __get__(self, instance, cls):
        return os.path.abspath(os.path.join(cls.APP_ROOT, os.pardir))


class FlaskKwargsDescriptor:
    def __get__(self, instance, cls):
        return {'template_folder': os.path.join(cls.PROJECT_ROOT, 'templates')}


class AppConfig:
    APP_ROOT: str = AppRootDescriptor()
    PROJECT_ROOT: str = ProjectRootDescriptor()
    FLASK_KWARGS: dict = FlaskKwargsDescriptor()
    BUNDLES = []
