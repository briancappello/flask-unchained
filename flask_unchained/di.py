import functools
import inspect
import networkx as nx

from types import FunctionType
from typing import *

from .exceptions import ServiceUsageError
from .string_utils import snake_case
from .utils import AttrDict, deep_getattr


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


class DependencyInjectionMixin:
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._initialized = False
        self._services_registry = {}
        self.extensions = AttrDict()
        self.services = AttrDict()

    def _reset(self):
        """
        this is for testing only!
        """
        self._initialized = False
        self._services_registry = {}
        self.extensions = AttrDict()
        self.services = AttrDict()

    def service(self, name: str = None):
        """
        decorator to mark something as a service
        """
        if self._initialized:
            from warnings import warn
            warn('Services have already been initialized. Please register '
                 f'{name} sooner.')
            return lambda x: x

        def wrapper(service):
            self.register_service(name, service)
            return service
        return wrapper

    def register_service(self, name: str, service: Any):
        """
        method to register a service
        """
        if not inspect.isclass(service):
            if hasattr(service, '__class__'):
                ensure_service_name(service.__class__, name)
            self.services[name] = service
            return

        if self._initialized:
            from warnings import warn
            warn('Services have already been initialized. Please register '
                 f'{name} sooner.')
            return

        self._services_registry[ensure_service_name(service, name)] = service

    def inject(self, *args):
        """
        Decorator to mark a callable as needing dependencies injected
        """
        used_without_parenthesis = len(args) and callable(args[0])
        has_explicit_args = len(args) and all(isinstance(x, str) for x in args)

        def wrapper(fn):
            cls = None
            if inspect.isclass(fn):
                cls = fn
                fn = fn.__init__

            # check if the fn has already been wrapped with injected
            if hasattr(fn, '__signature__'):
                if cls and not hasattr(cls, '__signature__'):
                    # this happens when both the class and its __init__ method
                    # where decorated with @inject. which would be silly, but,
                    # it should still work regardless
                    cls.__signature__ = fn.__signature__
                return cls or fn

            sig = inspect.signature(fn)

            # create a new function wrapping the original to inject params
            @functools.wraps(fn)
            def new_fn(*fn_args, **fn_kwargs):
                # figure out which params we need to inject (we don't want to
                # interfere with any params the user has passed manually)
                bound_args = sig.bind_partial(*fn_args, **fn_kwargs)
                required = set(sig.parameters.keys())
                have = set(bound_args.arguments.keys())
                need = required.difference(have)
                to_inject = (args if has_explicit_args
                             else set([k for k, v in sig.parameters.items()
                                       if v.default == injectable]))

                # try to inject needed params from extensions or services
                for param_name in to_inject:
                    if param_name not in need:
                        continue
                    if param_name in self.extensions:
                        fn_kwargs[param_name] = self.extensions[param_name]
                    elif param_name in self.services:
                        fn_kwargs[param_name] = self.services[param_name]

                # check to make sure we we're not missing anything required
                bound_args = sig.bind(*fn_args, **fn_kwargs)
                bound_args.apply_defaults()
                for k, v in bound_args.arguments.items():
                    if v == injectable:
                        di_name = new_fn.__di_name__
                        is_constructor = ('.' not in di_name
                                          and di_name != di_name.lower())
                        action = 'initialized' if is_constructor else 'called'
                        msg = f'{di_name} was {action} without the ' \
                              f'{k} parameter. Please supply it manually, or '\
                               'make sure it gets injected.'
                        raise ServiceUsageError(msg)

                return fn(*bound_args.args, **bound_args.kwargs)

            new_fn.__signature__ = sig
            new_fn.__di_name__ = fn.__name__

            if cls:
                cls.__init__ = new_fn
                cls.__signature__ = sig
                return cls
            return new_fn

        if used_without_parenthesis:
            return wrapper(args[0])
        return wrapper

    def _init_services(self):
        dag = nx.DiGraph()
        for name, service in self._services_registry.items():
            if not callable(service):
                self.services[name] = service
                continue

            dag.add_node(name)
            for param_name in inspect.signature(service).parameters:
                if (param_name in self.services
                        or param_name in self.extensions
                        or param_name in self._services_registry):
                    dag.add_edge(name, param_name)

        try:
            instantiation_order = reversed(list(nx.topological_sort(dag)))
        except nx.NetworkXUnfeasible:
            msg = 'Circular dependency detected between services'
            problem_graph = ', '.join([f'{a} -> {b}'
                                       for a, b in nx.find_cycle(dag)])
            raise Exception(f'{msg}: {problem_graph}')

        for name in instantiation_order:
            if name in self.services or name in self.extensions:
                continue

            service = self._services_registry[name]
            params = {n: self.extensions.get(n, self.services.get(n))
                      for n in dag.successors(name)}

            if not inspect.isclass(service):
                self.services[name] = functools.partial(service, **params)
            else:
                try:
                    self.services[name] = service(**params)
                except TypeError as e:
                    # FIXME this exception is too generic, need to better parse
                    # its string repr (eg, got unexpected keyword argument)
                    missing = str(e).rsplit(': ')[-1]
                    requester = f'{service.__module__}.{service.__name__}'
                    raise Exception(f'No service found with the name {missing} '
                                    f'(required by {requester})')

        self._initialized = True


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
