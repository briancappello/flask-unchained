import importlib
import inspect
import pkgutil

from flask import Flask
from types import FunctionType
from typing import Any, List, Optional, Tuple

from .bundle import Bundle
from .unchained import Unchained
from .utils import safe_import_module, snake_case


class ActionCategoryDescriptor:
    def __get__(self, instance, cls):
        return cls.name


class BundleOverrideModuleNameAttr:
    def __get__(self, instance, cls):
        if cls.bundle_module_name:
            return f'{cls.bundle_module_name}_module_name'


class HookNameDescriptor:
    def __get__(self, instance, cls):
        return snake_case(cls.__name__)


class AppFactoryMeta(type):
    def __new__(mcs, name, bases, clsdict):
        # automatically make action_table_converter a staticmethod
        converter = clsdict.get('action_table_converter')
        if isinstance(converter, FunctionType):
            clsdict['action_table_converter'] = staticmethod(converter)
        return super().__new__(mcs, name, bases, clsdict)


class AppFactoryHook(metaclass=AppFactoryMeta):
    name: str = HookNameDescriptor()
    priority: int = 50

    action_category: str = ActionCategoryDescriptor()
    action_table_columns = None
    action_table_converter = lambda x: x

    bundle_module_name: str = None
    bundle_override_module_name_attr: str = BundleOverrideModuleNameAttr()

    def __init__(self, unchained: Unchained, store=None):
        self.unchained = unchained
        if store:
            self.store = store

    def run_hook(self, app: Flask, bundles: List[Bundle]):
        objects = self.collect_from_bundles(bundles)
        self.process_objects(app, objects)

    def process_objects(self, app: Flask, objects: List[Tuple[str, Any]]):
        raise NotImplementedError

    def collect_from_bundles(self, bundles: List[Bundle],
                             ) -> List[Tuple[str, Any]]:
        objects = []
        for bundle in bundles:
            objects += self.collect_from_bundle(bundle)
        return objects

    def collect_from_bundle(self, bundle: Bundle) -> List[Tuple[str, Any]]:
        module = self.import_bundle_module(bundle)
        if not module:
            return []
        return self._collect_from_package(module)

    def _collect_from_package(self, module,
                              type_checker: Optional[FunctionType] = None,
                              ) -> List[Tuple[str, Any]]:
        type_checker = type_checker or self.type_check
        members = dict(inspect.getmembers(module, type_checker))

        # do not require everything be imported into a package's __init__.py
        # to be discoverable by hooks
        if pkgutil.get_loader(module).is_package(module.__name__):
            for loader, name, is_pkg in pkgutil.walk_packages(module.__path__):
                full_module_name = f'{module.__package__}.{name}'
                child_module = importlib.import_module(full_module_name)
                for member_name, member in inspect.getmembers(child_module,
                                                              type_checker):
                    if member_name not in members:
                        members[member_name] = member

        return list(members.items())

    def type_check(self, obj) -> bool:
        raise NotImplementedError

    def import_bundle_module(self, bundle: Bundle):
        if self.bundle_module_name is None:
            raise NotImplementedError('you must set the `bundle_module_name` '
                                      'class attribute on your hook to use '
                                      'this feature')
        return safe_import_module(self.get_module_name(bundle))

    def get_module_name(self, bundle: Bundle) -> str:
        module_name = getattr(bundle,
                              self.bundle_override_module_name_attr,
                              self.bundle_module_name)
        return f'{bundle.module_name}.{module_name}'

    def update_shell_context(self, ctx: dict):
        pass

    def log_action(self, data):
        self.unchained.log_action(self.action_category, data)
