import functools
import inspect

from py_meta_utils import (AbstractMetaOption, McsArgs, MetaOptionsFactory,
                           process_factory_meta_options, deep_getattr)
from types import FunctionType
from typing import *

from .constants import _DI_AUTOMATICALLY_HANDLED, _INJECT_CLS_ATTRS
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


def _ensure_service_name(service, name=None):
    default = snake_case(service.__name__)
    name = name or getattr(service, '__di_name__', default) or default

    try:
        setattr(service, '__di_name__', name)
    except AttributeError:
        pass  # must be a basic type, like str or int

    return name


def _inject_cls_attrs(_wrapped_fn=None, _call_super_for_cls: Optional[str] = None):
    def __init__(self, *args, **kwargs):
        from .unchained import unchained
        for param in self.__inject_cls_attrs__:
            if param == 'config':
                value = unchained._app.config
            elif param in unchained.extensions:
                value = unchained.extensions[param]
            elif param in unchained.services:
                value = unchained.services[param]
            else:
                raise Exception(f'No service found with the name {param} '
                                f'(required by {self.__class__.__name__})')
            setattr(self, param, value)

        if _call_super_for_cls:
            module, name = _call_super_for_cls.split(':')
            this_cls = [c for c in self.__class__.__mro__
                        if c.__module__ == module and c.__name__ == name][0]
            super(this_cls, self).__init__(*args, **kwargs)
        elif _wrapped_fn:
            _wrapped_fn(self, *args, **kwargs)

    if _wrapped_fn:
        return functools.wraps(_wrapped_fn)(__init__)
    return __init__


def _set_up_class_dependency_injection(mcs_args: McsArgs):
    mcs_args.clsdict[_DI_AUTOMATICALLY_HANDLED] = True

    cls_attrs_to_inject = [k for k, v in mcs_args.clsdict.items() if v == injectable]
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
                                        else _inject_cls_attrs(_wrapped_fn=init))
        mcs_args.clsdict['__signature__'] = init.__signature__

    for attr, value in mcs_args.clsdict.items():
        if isinstance(value, FunctionType):
            if not attr.startswith('__') and not hasattr(value, '__signature__'):
                from .unchained import unchained
                mcs_args.clsdict[attr] = unchained.inject()(value)
            value.__di_name__ = (mcs_args.name if value.__name__ == '__init__'
                                 else f'{mcs_args.name}.{value.__name__}')


class _ServiceMetaOptionsFactory(MetaOptionsFactory):
    _options = [AbstractMetaOption]


class _ServiceMetaclass(type):
    def __new__(mcs, name, bases, clsdict):
        mcs_args = McsArgs(mcs, name, bases, clsdict)
        _set_up_class_dependency_injection(mcs_args)
        process_factory_meta_options(
            mcs_args, default_factory_class=_ServiceMetaOptionsFactory)

        # extended concrete services should not inherit their super's di name
        if deep_getattr({}, bases, '__di_name__', None):
            clsdict['__di_name__'] = None

        return super().__new__(*mcs_args)

    def __init__(cls, name, bases, clsdict):
        super().__init__(name, bases, clsdict)
        if cls.Meta.abstract:
            return

        _ensure_service_name(cls)


class BaseService(metaclass=_ServiceMetaclass):
    """
    Base class for services in Flask Unchained. Automatically sets up dependency
    injection on the constructor of the subclass, and allows for your service to
    be automatically detected and used.
    """
    class Meta:
        abstract = True


__all__ = [
    'injectable',
    'BaseService',
]
