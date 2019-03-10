import importlib
import inspect
import pkgutil

from types import FunctionType
from typing import *

from .bundle import AppBundle, Bundle
from .exceptions import NameCollisionError
from .flask_unchained import FlaskUnchained
from .string_utils import snake_case
from .unchained import Unchained
from .utils import safe_import_module


class _BundleOverrideModuleNameAttrDescriptor:
    def __get__(self, instance, cls):
        if cls.bundle_module_name:
            return f'{cls.bundle_module_name}_module_name'.replace('.', '_')


class _HookNameDescriptor:
    def __get__(self, instance, cls):
        return snake_case(cls.__name__)


class AppFactoryHook:
    """
    Base class for hooks. It has one entry point, :meth:`run_hook`, which can be
    overridden to completely customize the behavior of the subclass. The default
    behavior is to look for objects in :attr:`bundle_module_name` which pass the
    result of :meth:`type_check`. These objects are collected from all bundles
    into a dictionary with keys the result of :meth:`key_name`, starting from
    the base-most bundle, allowing bundle subclasses to override objects with
    the same name from earlier bundles.

    Subclasses should implement at a minimum :attr:`bundle_module_name`,
    :meth:`process_objects`, and :meth:`type_check`. You may also need to set
    one or both of :attr:`run_before` or :attr:`run_after`. Also of interest,
    hooks can store objects on their bundle's instance, using :attr:`bundle`.
    Hooks can also modify the shell context using :meth:`update_shell_context`.
    """

    name: str = _HookNameDescriptor()
    """
    The name of this hook. Defaults to the snake-cased class name.
    """

    run_before: Union[List[str], Tuple[str, ...]] = ()
    """
    An optional list of hook names that this hook must run *before*.
    """

    run_after: Union[List[str], Tuple[str, ...]] = ()
    """
    An optional list of hook names that this hook must run *after*.
    """

    bundle_module_name: str = None
    """
    The default module name this hook will load from in bundles. Should be set to
    ``None`` if your hook does not use that default functionality.
    """

    bundle_override_module_name_attr: str = _BundleOverrideModuleNameAttrDescriptor()
    """
    The attribute name that bundles can set on themselves to override the module
    this hook will load from for that bundle.
    """

    discover_from_bundle_superclasses: bool = True
    """
    Whether or not to search the whole bundle hierarchy for objects.
    """

    limit_discovery_to_local_declarations: bool = True
    """
    Whether or not to only include objects declared within bundles (ie not
    imported from other places, like third-party code).
    """

    def __init__(self, unchained: Unchained, bundle=None):
        self.unchained = unchained
        """
        The :class:`~flask_unchained.Unchained` extension instance.
        """

        self.bundle = bundle
        """
        The :class:`~flask_unchained.Bundle` instance this hook is from (if any).
        """

    def run_hook(self, app: FlaskUnchained, bundles: List[Bundle]):
        """
        Hook entry point. Override to disable standard behavior of iterating
        over bundles to discover objects and processing them.
        """
        self.process_objects(app, self.collect_from_bundles(bundles))

    def process_objects(self, app: FlaskUnchained, objects: Dict[str, Any]):
        """
        Implement to do stuff with discovered objects (eg, registering them with
        the app instance).
        """
        raise NotImplementedError

    def collect_from_bundles(self, bundles: List[Bundle]) -> Dict[str, Any]:
        """
        Collect objects where :meth:`type_check` returns ``True`` from bundles.
        Names (keys) are expected to be unique across bundles, except for the
        app bundle, which can override anything from other bundles.
        """
        all_objects = {}  # all discovered objects
        key_bundles = {}  # lookup of which bundle a key came from
        object_keys = set()  # keys in all_objects, used to ensure uniqueness
        for bundle in bundles:
            from_bundle = self.collect_from_bundle(bundle)
            if isinstance(bundle, AppBundle):
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

    def collect_from_bundle(self, bundle: Bundle) -> Dict[str, Any]:
        """
        Collect objects where :meth:`type_check` returns ``True`` from bundles.
        Bundle subclasses can override objects discovered in superclass bundles.
        """
        members = {}
        hierarchy = ([bundle] if not self.discover_from_bundle_superclasses
                     else bundle._iter_class_hierarchy())
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
        Discover objects passing :meth:`type_check` by walking through all the
        child modules/packages in the given module (ie, do not require modules
        to import everything into their ``__init__.py`` for it to be discovered)
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
            # FIXME
            # currently, no hooks depend on this working correctly, however
            # ``obj.__module__.startswith(module.__name__)`` isn't right for
            # instance variables (it works fine for classes, but instances seem
            # to keep the __module__ of their *class*, not where they themselves
            # were defined/instantiated)
            #
            # possible solution, should probably be done within a metaclass __init__ if
            # it's ever needed:
            #
            # https://stackoverflow.com/questions/14413025/how-can-i-find-out-where-an-object-has-been-instantiated#14413108
            if isinstance(obj, type):
                is_local_declaration = obj.__module__.startswith(module.__name__)
            else:
                is_local_declaration = False
                if self.limit_discovery_to_local_declarations:
                    raise NotImplementedError

            if is_local_declaration or not self.limit_discovery_to_local_declarations:
                yield self.key_name(name, obj), obj

    def key_name(self, name: str, obj: Any) -> str:
        """
        Override to use a custom key to determine uniqueness/overriding.
        """
        return name

    def type_check(self, obj: Any) -> bool:
        """
        Implement to determine which objects in a module should be processed
        by this hook.
        """
        raise NotImplementedError

    @classmethod
    def import_bundle_module(cls, bundle: Bundle):
        if cls.bundle_module_name is None:
            raise NotImplementedError('you must set the `bundle_module_name` '
                                      'class attribute on your hook to use '
                                      'this feature')
        return safe_import_module(cls.get_module_name(bundle))

    @classmethod
    def get_module_name(cls, bundle: Bundle) -> str:
        return f'{bundle.module_name}.{cls.get_bundle_module_name(bundle)}'

    @classmethod
    def get_bundle_module_name(cls, bundle: Bundle) -> str:
        return getattr(bundle,
                       cls.bundle_override_module_name_attr,
                       cls.bundle_module_name)

    def update_shell_context(self, ctx: dict):
        """
        Implement to add objects to the cli shell context.
        """
        pass


__all__ = [
    'AppFactoryHook',
]
