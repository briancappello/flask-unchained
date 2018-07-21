import os
import sys


class AppRootDescriptor:
    def __get__(self, instance, cls):
        return os.path.dirname(sys.modules[cls.__module__].__file__)


class ProjectRootDescriptor:
    def __get__(self, instance, cls):
        return os.path.abspath(os.path.join(cls.APP_ROOT, os.pardir))


class TemplateFolderDescriptor:
    def __get__(self, instance, cls):
        return os.path.join(cls.PROJECT_ROOT, 'templates')


class StaticFolderDescriptor:
    def __get__(self, instance, cls):
        return os.path.join(cls.PROJECT_ROOT, 'static')


class AppConfig:
    APP_ROOT: str = AppRootDescriptor()
    PROJECT_ROOT: str = ProjectRootDescriptor()

    TEMPLATE_FOLDER: str = TemplateFolderDescriptor()
    STATIC_FOLDER: str = StaticFolderDescriptor()
    STATIC_URL_PATH: str = '/static'
