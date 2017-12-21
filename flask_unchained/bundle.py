from .utils import right_replace, snake_case


def _normalize_module_name(module_name):
    if module_name.endswith('.bundle'):
        return right_replace(module_name, '.bundle', '')
    return module_name


class ModuleNameDescriptor:
    def __get__(self, instance, cls):
        return _normalize_module_name(cls.__module__)


class NameDescriptor:
    def __get__(self, instance, cls):
        if cls.app_bundle:
            if '.' not in cls.module_name:
                return cls.module_name
            return cls.module_name.rsplit('.', 1)[-1]
        return snake_case(cls.__name__)


class BundleMeta(type):
    def __new__(mcs, name, bases, clsdict):
        # check if the user explicitly set module_name
        module_name = clsdict.get('module_name')
        if isinstance(module_name, str):
            clsdict['module_name'] = _normalize_module_name(module_name)
        return super().__new__(mcs, name, bases, clsdict)

    def __repr__(cls):
        return f'class <Bundle name={cls.name!r} module={cls.module_name!r}>'


class Bundle(metaclass=BundleMeta):
    app_bundle: bool = False
    """Whether or not this bundle is the top-level application bundle"""

    module_name: str = ModuleNameDescriptor()
    """Top-level module name of the bundle (dot notation)"""

    name: str = NameDescriptor()
    """Name of the bundle. Defaults to the snake cased class name"""

    hooks = []
    """A list of AppFactoryHook classes to register to be run by AppFactory"""

    store = None
    """
    An optional dict or class instance to add to the unchained extension,
    useful for hooks that need to share data between themselves, or to store
    data that persists once the app has been brought up by the factory. The
    store instance is available as an attribute at unchained.<bundle_name>
    """
