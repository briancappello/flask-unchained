import importlib
import inspect
import pkgutil

from types import FunctionType, ModuleType
from typing import *

from .bundles import AppBundle, Bundle
from .exceptions import NameCollisionError
from .flask_unchained import FlaskUnchained
from .string_utils import snake_case
from .unchained import Unchained
from .utils import safe_import_module
from ._compat import is_local_proxy


class _BundleOverrideModuleNamesAttrDescriptor:
    def __get__(self, instance, cls):
        if cls.require_exactly_one_bundle_module:
            return f'{cls.bundle_module_name}_module_name'
        elif cls.bundle_module_names:
            return f'{cls.bundle_module_names[0]}_module_names'.replace('.', '_')
        elif cls.bundle_module_name:
            raise RuntimeError(
                f'To use `bundle_module_name` on {cls.__name__}, you must also set '
                f'`{cls.__name__}.require_exactly_one_bundle_module = True`')
        return None


class _HookNameDescriptor:
    def __get__(self, instance, cls):
        return snake_case(cls.__name__)


class AppFactoryHook:
    """
    Base class for hooks.

    Hooks have one entry point, :meth:`run_hook`, which can be
    overridden to completely customize the behavior of the subclass. The default
    behavior is to look for objects in :attr:`bundle_module_names` which pass the
    result of :meth:`type_check`. These objects are collected from all bundles
    into a dictionary with keys the result of :meth:`key_name`, starting from
    the base-most bundle, allowing bundle subclasses to override objects with
    the same name from earlier bundles.

    Subclasses should implement at a minimum :attr:`bundle_module_names`,
    :meth:`process_objects`, and :meth:`type_check`. You may also need to set
    one or both of :attr:`run_before` or :attr:`run_after`. Also of interest,
    hooks can store objects on their bundle's instance, using :attr:`bundle`.
    Hooks can also modify the shell context using :meth:`update_shell_context`.
    """

    name: str = _HookNameDescriptor()
    """
    The name of this hook. Defaults to the snake_cased class name.
    """

    run_before: Union[List[str], Tuple[str, ...]] = ()
    """
    An optional list of hook names that this hook must run *before*.
    """

    run_after: Union[List[str], Tuple[str, ...]] = ()
    """
    An optional list of hook names that this hook must run *after*.
    """

    bundle_module_name: Optional[str] = None
    """
    If :attr:`require_exactly_one_bundle_module` is True, only load from this
    module name in bundles. Should be set to ``None`` if your hook does not use that
    default functionality.
    """

    bundle_module_names: Optional[Union[List[str], Tuple[str, ...]]] = None
    """
    A list of the default module names this hook will load from in bundles. Should
    be set to ``None`` if your hook does not use that default functionality (or
    :attr:`require_exactly_one_bundle_module` is True).
    """

    require_exactly_one_bundle_module: bool = False
    """
    Whether or not to require that there must be exactly one module name to load from
    in bundles.
    """

    bundle_override_module_names_attr: str = _BundleOverrideModuleNamesAttrDescriptor()
    """
    The attribute name that bundles can set on themselves to override the module(s)
    this hook will load from for that bundle. The defaults are as follows:

    If :attr:`require_exactly_one_bundle_module` and :attr:`bundle_module_name` are set,
    use ``f'{YourHook.bundle_module_name}_module_name'``.

    Otherwise if :attr:`bundle_module_names` is set, we use the same f-string, just with
    the first module name listed in :attr:`bundle_module_names`.

    If neither of :attr:`bundle_module_name` or :attr:`bundle_module_names` is set, then
    this will be ``None``.
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

    def __init__(self, unchained: Unchained, bundle: Optional[Bundle] = None):
        self.unchained = unchained
        """
        The :class:`~flask_unchained.Unchained` extension instance.
        """

        self.bundle = bundle
        """
        The :class:`~flask_unchained.Bundle` instance this hook is from (if any).
        """

    def run_hook(self,
                 app: FlaskUnchained,
                 bundles: List[Bundle],
                 unchained_config: Optional[Dict[str, Any]] = None,
                 ) -> None:
        """
        Hook entry point. Override to disable standard behavior of iterating
        over bundles to discover objects and processing them.
        """
        self.process_objects(app, self.collect_from_bundles(bundles))

    def process_objects(self, app: FlaskUnchained, objects: Dict[str, Any]) -> None:
        """
        Implement to do stuff with discovered objects (eg, registering them with
        the app instance).
        """
        raise NotImplementedError

    def collect_from_bundles(self,
                             bundles: List[Bundle],
                             *,
                             _initial_objects: Optional[Dict[str, Any]] = None,
                             ) -> Dict[str, Any]:
        """
        Collect objects where :meth:`type_check` returns ``True`` from bundles.
        Discovered names (keys, typically the class names) are expected to be unique
        across bundle hierarchies, except for the app bundle, which can override
        anything from other bundles.
        """
        all_objects = _initial_objects or {}  # all discovered objects
        key_bundles = {}  # lookup of which bundle a key in all_objects came from
        object_keys = set(all_objects.keys())  # used to ensure key name uniqueness
        for bundle in bundles:
            from_bundle = self.collect_from_bundle(bundle)
            if isinstance(bundle, AppBundle):
                # app_bundle is last and allowed to override everything
                all_objects.update(from_bundle)
                return all_objects

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
        for b in hierarchy:
            last_module = None
            from_this_bundle = set()
            for module in self.import_bundle_modules(b):
                found = self._collect_from_package(module)
                name_collisions = from_this_bundle & set(found.keys())
                if name_collisions:
                    raise NameCollisionError(
                        f'Name conflict in the {bundle.name} bundle hierarchy: '
                        f'The objects named {", ".join(name_collisions)} '
                        f'in {module.__name__} '
                        f'collide with those from {last_module.__name__}')
                members.update(found)
                last_module = module
                from_this_bundle.update(found.keys())
        return members

    def _collect_from_package(self,
                              module: ModuleType,
                              type_checker: Optional[Callable[[Any], bool]] = None,
                              ) -> Dict[str, Any]:
        """
        Discover objects passing :meth:`type_check` by walking through all the
        child modules/packages in the given module (ie, do not require packages
        to import everything into their ``__init__.py`` for it to be discovered)
        """
        def type_check_wrapper(obj: Any) -> bool:
            if is_local_proxy(obj):
                return False
            return (type_checker or self.type_check)(obj)

        members = dict(self._get_members(module, type_check_wrapper))

        # if the passed module is a package, also get members from child modules
        if importlib.util.find_spec(module.__name__).submodule_search_locations:
            for _, name, _ in pkgutil.walk_packages(module.__path__):
                child_module_name = f'{module.__package__}.{name}'
                child_module = importlib.import_module(child_module_name)
                for key, obj in self._get_members(child_module, type_check_wrapper):
                    if key not in members:
                        members[key] = obj

        return members

    def _get_members(self,
                     module: ModuleType,
                     type_checker: Callable[[Any], bool],
                     ) -> List[Tuple[str, Any]]:
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
            if isinstance(obj, (type, FunctionType)):
                is_local_declaration = obj.__module__.startswith(module.__name__)
            else:
                is_local_declaration = False
                if self.limit_discovery_to_local_declarations:
                    raise NotImplementedError

            if is_local_declaration or not self.limit_discovery_to_local_declarations:
                yield self.key_name(name, obj), obj

    def key_name(self,
                 name: str,
                 obj: Any,  # skipcq: PYL-W0613 (unused arg)
                 ) -> str:
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
    def import_bundle_modules(cls, bundle: Bundle) -> List[ModuleType]:
        """
        Safe-import the modules in a bundle for this hook to load from.
        """
        modules = [safe_import_module(module_name)
                   for module_name in cls.get_module_names(bundle)]
        return [m for m in modules if m]

    @classmethod
    def get_module_names(cls, bundle: Bundle) -> List[str]:
        """
        The list of fully-qualified module names for a bundle this hook should
        load from.
        """
        if bundle.is_single_module:
            return [bundle.module_name]
        return [bundle.module_name if name == '__init__' else f'{bundle.module_name}.{name}'
                for name in cls.get_bundle_module_names(bundle)]

    @classmethod
    def get_bundle_module_names(cls, bundle: Bundle) -> List[str]:
        """
        The list of module names inside a bundle this hook should load from.
        """
        if bundle.is_single_module:
            return ['__init__']

        # check to make sure the hook is configured correctly
        if cls.require_exactly_one_bundle_module and cls.bundle_module_name is None:
            raise RuntimeError(f'you must set the `bundle_module_name` class attribute '
                               f'on {cls.__module__}.{cls.__name__} to use this feature.')
        elif not cls.require_exactly_one_bundle_module and cls.bundle_module_names is None:
            raise RuntimeError(f'you must set the `bundle_module_names` class attribute '
                               f'on {cls.__module__}.{cls.__name__} to use this feature.')

        module_names = getattr(bundle, cls.bundle_override_module_names_attr, None)
        if module_names is None:
            if bundle.default_load_from_module_name:
                module_names = bundle.default_load_from_module_name
            elif cls.require_exactly_one_bundle_module:
                module_names = cls.bundle_module_name
            else:
                module_names = cls.bundle_module_names

        # check to make sure the user's bundle override module name(s) attribute is correct
        if cls.require_exactly_one_bundle_module and not isinstance(module_names, str):
            raise ValueError(f'The {cls.bundle_override_module_names_attr} attribute '
                             f'on {bundle.module_name}.{bundle.__class__.__name__} '
                             f'must be a string for exactly one module name.')

        if isinstance(module_names, str):
            return [module_names]
        return module_names

    def update_shell_context(self, ctx: Dict[str, Any]) -> None:
        """
        Implement to add objects to the CLI shell context.
        """
        pass


__all__ = [
    'AppFactoryHook',
]
