from py_meta_utils import (AbstractMetaOption, McsArgs, MetaOptionsFactory,
                           apply_factory_meta_options, deep_getattr)
from types import FunctionType

from .string_utils import snake_case


injectable = 'INJECTABLE_PARAMETER'
"""
Use this to mark a service parameter as injectable. For example::

    class MyService(BaseService):
        def __init__(self, a_dependency: ADependency = injectable):
            self.a_dependency = a_dependency

This allows MyService to be used in two ways::

    # 1. using dependency injection with Flask Unchained
    my_service = MyService()

    # 2. overriding the dependency injection (or used without Flask Unchained)
    a_dependency = ADependency()
    my_service = MyService(a_dependency)

    # but, if you try to use it without Flask Unchained and without parameters:
    my_service = MyService()  # raises ServiceUsageError
"""


def ensure_service_name(service, name=None):
    default = snake_case(service.__name__)
    name = name or getattr(service, '__di_name__', default) or default

    try:
        setattr(service, '__di_name__', name)
    except AttributeError:
        pass  # must be a basic type, like str or int

    return name


def set_up_class_dependency_injection(mcs_args: McsArgs):
    if '__init__' in mcs_args.clsdict:
        from .unchained import unchained
        init = unchained.inject()(mcs_args.clsdict['__init__'])
        mcs_args.clsdict['__init__'] = init
        mcs_args.clsdict['__signature__'] = init.__signature__

    for attr, fn in mcs_args.clsdict.items():
        if isinstance(fn, FunctionType) and hasattr(fn, '__signature__'):
            fn.__di_name__ = (mcs_args.name if fn.__name__ == '__init__'
                              else f'{mcs_args.name}.{fn.__name__}')


class ServiceMetaOptionsFactory(MetaOptionsFactory):
    options = [AbstractMetaOption]


class ServiceMeta(type):
    def __new__(mcs, name, bases, clsdict):
        mcs_args = McsArgs(mcs, name, bases, clsdict)
        set_up_class_dependency_injection(mcs_args)
        apply_factory_meta_options(
            mcs_args, default_factory_class=ServiceMetaOptionsFactory)

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
    """
    Base class for services in Flask Unchained. Automatically sets up dependency
    injection on the constructor of the subclass, and allows for your service to
    be automatically detected and used.
    """
    class Meta:
        abstract = True
