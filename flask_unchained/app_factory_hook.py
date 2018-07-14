import importlib
import inspect
import pkgutil

from flask import Flask
from types import FunctionType
from typing import *

from .bundle import AppBundle, Bundle
from .exceptions import NameCollisionError
from .string_utils import snake_case
from .unchained import Unchained
from .utils import safe_import_module


class ActionCategoryDescriptor:
    def __get__(self, instance, cls):
        return cls.name


class BundleOverrideModuleNameAttrDescriptor:
    def __get__(self, instance, cls):
        if cls.bundle_module_name:
            return f'{cls.bundle_module_name}_module_name'.replace('.', '_')


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
    run_after: Union[List[str], Tuple[str, ...]] = []
    run_before: Union[List[str], Tuple[str, ...]] = []

    action_category: str = ActionCategoryDescriptor()
    action_table_columns: Union[List[str], Tuple[str, ...]] = None
    action_table_converter: FunctionType = lambda x: x

    bundle_module_name: str = None
    bundle_override_module_name_attr: str = \
        BundleOverrideModuleNameAttrDescriptor()

    _discover_from_bundle_superclasses: bool = True
    """
    whether or not to search the whole bundle inheritance hierarchy for objects
    """

    _limit_discovery_to_local_declarations: bool = True
    """
    whether or not to only include objects declared within bundles (ie not
    imported from other places, like third-party code)
    """

    def __init__(self, unchained: Unchained, store=None):
        self.unchained = unchained
        self.store = store

    def run_hook(self, app: Flask, bundles: List[Type[Bundle]]):
        """
        hook entrance point. override to disable standard behavior of iterating
        over bundles to discover objects and processing them
        """
        self.process_objects(app, self.collect_from_bundles(bundles))

    def process_objects(self, app: Flask, objects: Dict[str, Any]):
        """
        implement to do stuff with discovered objects (typically registering
        them with the app instance)
        """
        raise NotImplementedError

    def collect_from_bundles(self, bundles: List[Type[Bundle]],
                             ) -> Dict[str, Any]:
        """
        collect (objects where self.type_check returns True) from bundles.
        names (keys) are expected to be unique across bundles, except for the
        app bundle, which can override anything from other bundles.
        """
        all_objects = {}  # all discovered objects
        key_bundles = {}  # lookup of which bundle a key came from
        object_keys = set()  # keys in all_objects, used to ensure uniqueness
        for bundle in bundles:
            from_bundle = self.collect_from_bundle(bundle)
            if issubclass(bundle, AppBundle):
                all_objects.update(from_bundle)
                break  # app_bundle is last, no need to update keys

            from_bundle_keys = set(from_bundle.keys())
            conflicts = object_keys.intersection(from_bundle_keys)
            if conflicts:
                msg = [f'{self.name} from {bundle.name} conflict with '
                       f'previously registered {self.name}:']
                for key in conflicts:
                    msg.append(f'{key} from {key_bundles[key].name}')
                raise NameCollisionError('\n'.join(msg))

            all_objects.update(from_bundle)
            object_keys = object_keys.union(from_bundle_keys)
            key_bundles.update({k: bundle for k in from_bundle_keys})

        return all_objects

    def collect_from_bundle(self, bundle: Type[Bundle]) -> Dict[str, Any]:
        """
        collect (objects where self.type_check returns True) from bundles.
        bundle subclasses can override objects discovered in superclass bundles.
        """
        members = {}
        hierarchy = ([bundle] if not self._discover_from_bundle_superclasses
                     else bundle.iter_class_hierarchy())
        for bundle in hierarchy:
            module = self.import_bundle_module(bundle)
            if not module:
                continue
            members.update(self._collect_from_package(module))
        return members

    def _collect_from_package(self, module,
                              type_checker: Optional[FunctionType] = None,
                              ) -> Dict[str, Any]:
        """
        discover objects passing self.type_check by walking through all the
        child modules/packages in the given module (ie, do not require modules
        to import everything into their __init__.py for it to be discovered)
        """
        type_checker = type_checker or self.type_check
        members = dict(self._get_members(module, type_checker))

        if pkgutil.get_loader(module).is_package(module.__name__):
            for loader, name, is_pkg in pkgutil.walk_packages(module.__path__):
                child_module_name = f'{module.__package__}.{name}'
                child_module = importlib.import_module(child_module_name)
                for key, obj in self._get_members(child_module, type_checker):
                    if key not in members:
                        members[key] = obj

        return members

    def _get_members(self, module, type_checker) -> List[Tuple[str, Any]]:
        for name, obj in inspect.getmembers(module, type_checker):
            if inspect.isclass(obj):
                is_local_declaration = obj.__module__ in module.__name__
            else:
                is_local_declaration = False  # FIXME this is shit
                if self._limit_discovery_to_local_declarations:
                    print('hrm crap', self.__class__.__name__)

            # FIXME obj.__module__ in module.__name__ probably isn't right
            # for instance variables (works fine for classes, but instances
            # seem to keep the __module__ of their *class*, not where they
            # themselves were defined. which is fucking garbage for this.)
            #
            # possible solution, should probably be done within a metaclass __init__ if
            # it's ever needed (currently, no hooks depend on this working correctly)
            #
            # https://stackoverflow.com/questions/14413025/how-can-i-find-out-where-an-object-has-been-instantiated#14413108
            if not self._limit_discovery_to_local_declarations or is_local_declaration:
                yield self.key_name(name, obj), obj

    def key_name(self, name, obj):
        """
        override to use a custom key to determine uniqueness/overriding
        """
        return name

    def type_check(self, obj: Any) -> bool:
        """
        implement to determine which objects in a module should be processed
        by this hook
        """
        raise NotImplementedError

    def import_bundle_module(self, bundle: Type[Bundle]):
        if self.bundle_module_name is None:
            raise NotImplementedError('you must set the `bundle_module_name` '
                                      'class attribute on your hook to use '
                                      'this feature')
        return safe_import_module(self.get_module_name(bundle))

    def get_module_name(self, bundle: Type[Bundle]) -> str:
        module_name = getattr(bundle,
                              self.bundle_override_module_name_attr,
                              self.bundle_module_name)
        return f'{bundle.module_name}.{module_name}'

    def update_shell_context(self, ctx: dict):
        """
        implement to add objects to the cli shell context
        """
        pass

    def log_action(self, data):
        self.unchained.log_action(self.action_category, data)
