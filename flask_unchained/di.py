from types import FunctionType

from .string_utils import snake_case
from .utils import deep_getattr


injectable = 'INJECTABLE_PARAMETER'
"""
Use this to mark a service parameter as injectable. For example::

    class MyService(BaseService):
        def __init__(self, a_dependency: ADependency = injectable):
            self.a_dependency = a_dependency

This allows MyService to be used in one of three ways::

    # using dependency injection with flask unchained
    my_service = MyService()

    # overriding the dependency injection (or used without flask unchained)
    a_dependency = ADependency()
    my_service = MyService(a_dependency)

    # but try to use it without flask unchained and without parameters
    my_service = MyService()
    my_service.a_dependency.anything  # raises ServiceUsageError
"""


def ensure_service_name(service, name=None):
    default = snake_case(service.__name__)
    name = name or getattr(service, '__di_name__', default) or default

    try:
        setattr(service, '__di_name__', name)
    except AttributeError:
        pass  # must be a basic type, like str or int

    return name


def setup_class_dependency_injection(class_name, clsdict):
    if '__init__' in clsdict:
        from .unchained import unchained
        init = unchained.inject()(clsdict['__init__'])
        clsdict['__init__'] = init
        clsdict['__signature__'] = init.__signature__

    for attr, fn in clsdict.items():
        if isinstance(fn, FunctionType) and hasattr(fn, '__signature__'):
            fn.__di_name__ = (class_name if fn.__name__ == '__init__'
                              else f'{class_name}.{fn.__name__}')


class ServiceMeta(type):
    def __new__(mcs, name, bases, clsdict):
        setup_class_dependency_injection(name, clsdict)

        # extended concrete services should not inherit their super's di name
        if deep_getattr({}, bases, '__di_name__', None):
            clsdict['__di_name__'] = None

        return super().__new__(mcs, name, bases, clsdict)

    def __init__(cls, name, bases, clsdict):
        super().__init__(name, bases, clsdict)
        if '__abstract__' in clsdict:
            return

        ensure_service_name(cls)


class BaseService(metaclass=ServiceMeta):
    __abstract__ = True
