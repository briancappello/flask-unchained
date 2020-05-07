import functools
import inspect

from py_meta_utils import (AbstractMetaOption, McsArgs, MetaOptionsFactory,
                           process_factory_meta_options, deep_getattr, _missing)
from types import FunctionType
from typing import *

from .constants import _DI_AUTOMATICALLY_HANDLED, _INJECT_CLS_ATTRS
from .exceptions import ServiceUsageError
from .string_utils import snake_case


injectable = 'INJECTABLE_PARAMETER'
"""
Use this to mark a service parameter as injectable. For example::

    class MyService(Service):
        a_dependency: ADependency = injectable

This allows MyService to be used in two ways::

    # 1. using dependency injection with Flask Unchained
    my_service = MyService()

    # 2. overriding the dependency injection (or used without Flask Unchained)
    a_dependency = ADependency()
    my_service = MyService(a_dependency)

    # but, if you try to use it without Flask Unchained and without parameters:
    my_service = MyService()  # raises ServiceUsageError
"""


def _ensure_service_name(service, name=None):
    default = snake_case(service.__name__)
    name = name or getattr(service, '__di_name__', default) or default

    try:
        setattr(service, '__di_name__', name)
    except AttributeError:
        pass  # must be a basic type, like str or int

    return name


def _get_injected_value(
    unchained_ext,
    param_name: str,
    requested_by: str = None,
    throw: bool = True,
):
    value = _missing
    if param_name == 'config':
        value = unchained_ext._app.config
    elif param_name in unchained_ext.extensions:
        value = unchained_ext.extensions[param_name]
    elif param_name in unchained_ext.services:
        value = unchained_ext.services[param_name]
    elif throw:
        if not requested_by:
            raise RuntimeError('You must pass `requested_by` when `throw` is True')
        raise ServiceUsageError(f'No extension or service was found with the name '
                                f'{param_name} (required by {requested_by})')
    return value


def _inject_cls_attrs(_wrapped_constructor: Optional[callable] = None,
                      _call_super_for_cls: Optional[str] = None,
                      ) -> callable:
    def __init__(self, *args, **kwargs):
        from .unchained import unchained

        for param in getattr(self, _INJECT_CLS_ATTRS):
            setattr(self, param, _get_injected_value(
                unchained_ext=unchained,
                param_name=param,
                requested_by=self.__class__.__name__,
            ))

        if _call_super_for_cls:
            module, name = _call_super_for_cls.split(':')
            this_cls = [c for c in self.__class__.__mro__
                        if c.__module__ == module and c.__name__ == name][0]
            super(this_cls, self).__init__(*args, **kwargs)
        elif _wrapped_constructor:
            _wrapped_constructor(self, *args, **kwargs)

    if _wrapped_constructor:
        return functools.wraps(_wrapped_constructor)(__init__)
    return __init__


def _set_up_class_dependency_injection(mcs_args: McsArgs):
    mcs_args.clsdict[_DI_AUTOMATICALLY_HANDLED] = True

    cls_attrs_to_inject = [k for k, v in mcs_args.clsdict.items()
                           if isinstance(v, str) and v == injectable]
    try:
        mcs_args.clsdict[_INJECT_CLS_ATTRS] = \
            cls_attrs_to_inject + mcs_args.getattr(_INJECT_CLS_ATTRS, [])
    except TypeError as e:
        if 'can only concatenate list (not "OptionalMetaclass") to list' not in str(e):
            raise e
        mcs_args.clsdict[_INJECT_CLS_ATTRS] = cls_attrs_to_inject

    if '__init__' not in mcs_args.clsdict and cls_attrs_to_inject:
        init = _inject_cls_attrs(
            _call_super_for_cls=f'{mcs_args.module}:{mcs_args.name}')
        init.__di_name__ = mcs_args.name
        init.__signature__ = inspect.signature(object)
        mcs_args.clsdict['__init__'] = init
        mcs_args.clsdict['__signature__'] = init.__signature__
    elif '__init__' in mcs_args.clsdict:
        from .unchained import unchained
        init = unchained.inject()(mcs_args.clsdict['__init__'])
        init.__di_name__ = mcs_args.name
        mcs_args.clsdict['__init__'] = (init if not cls_attrs_to_inject
                                        else _inject_cls_attrs(_wrapped_constructor=init))
        mcs_args.clsdict['__signature__'] = init.__signature__

    # when the user has wrapped a method with unchained.inject(), add our
    # class name to the __di_name__ (which typically will be the fn name)
    for name, method in mcs_args.clsdict.items():
        if (name != '__init__'
                and isinstance(method, FunctionType)
                and hasattr(method, '__di_name__')):
            setattr(method, '__di_name__', f'{mcs_args.name}.{method.__di_name__}')


class ServiceMetaOptionsFactory(MetaOptionsFactory):
    _options = [AbstractMetaOption]


class ServiceMetaclass(type):
    def __new__(mcs, name, bases, clsdict):
        mcs_args = McsArgs(mcs, name, bases, clsdict)
        _set_up_class_dependency_injection(mcs_args)
        process_factory_meta_options(
            mcs_args, default_factory_class=ServiceMetaOptionsFactory)

        # extended concrete services should not inherit their super's di name
        if deep_getattr({}, bases, '__di_name__', None):
            clsdict['__di_name__'] = None

        return super().__new__(*mcs_args)

    def __init__(cls, name, bases, clsdict):
        super().__init__(name, bases, clsdict)
        if cls.Meta.abstract:
            return

        _ensure_service_name(cls)


class Service(metaclass=ServiceMetaclass):
    """
    Base class for services. Automatically sets up dependency injection on the
    constructor of the subclass, and allows for your service to be automatically
    detected and used.
    """
    class Meta:
        abstract = True


__all__ = [
    'injectable',
    'Service',
    'ServiceMetaclass',
    'ServiceMetaOptionsFactory',
]
