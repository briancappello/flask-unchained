import inspect

from typing import List, Tuple

from flask import Flask

from .bundle import Bundle
from .utils import get_boolean_env, safe_import_module


class BundleOverrideModuleNameAttr:
    def __get__(self, instance, cls):
        return f'{cls.bundle_module_name}_module_name'


class AppFactoryHook:
    priority: int = 50

    bundle_module_name: str = None
    bundle_override_module_name_attr: str = BundleOverrideModuleNameAttr()

    def __init__(self, unchained, store_name=None):
        self.unchained = unchained
        if store_name:
            self.store = getattr(unchained, store_name, None)
        self.verbose = get_boolean_env('FLASK_UNCHAINED_VERBOSE', False)
        if not self.bundle_module_name:
            raise AttributeError(f'{self.__class__.__name__} is missing a '
                                 f'`bundle_module_name` attribute')

    def run_hook(self, app: Flask, bundles: List[Bundle]):
        objects = self.collect_from_bundles(bundles)
        self.process_objects(app, objects)

    def process_objects(self, app: Flask, objects):
        raise NotImplementedError

    def collect_from_bundles(self, bundles: List[Bundle]) -> List[Tuple[str, object]]:
        objects = []
        for bundle in bundles:
            objects += self.collect_from_bundle(bundle)
        return objects

    def collect_from_bundle(self, bundle: Bundle) -> List[Tuple[str, object]]:
        module = self.import_bundle_module(bundle)
        if not module:
            return []
        return inspect.getmembers(module, self.type_check)

    def type_check(self, obj) -> bool:
        raise NotImplementedError

    def import_bundle_module(self, bundle: Bundle):
        if self.bundle_module_name is None:
            raise NotImplementedError('you must set the `bundle_module_name` '
                                      'class attribute on your hook to use '
                                      'this feature')
        return safe_import_module(self.get_module_name(bundle))

    def get_module_name(self, bundle: Bundle):
        module_name = getattr(bundle,
                              self.bundle_override_module_name_attr,
                              self.bundle_module_name)
        return f'{bundle.module_name}.{module_name}'

    def update_shell_context(self, ctx: dict):
        pass

    def log_msg(self, category, msg: str):
        self.unchained.log_msg(category, msg)
