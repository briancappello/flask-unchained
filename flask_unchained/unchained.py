import inspect
import networkx as nx

from collections import defaultdict, namedtuple
from datetime import datetime
from flask import Flask
from functools import partial, wraps
from typing import List, Optional, Type

from .app_config import AppConfig
from .bundle import Bundle
from .di import ensure_service_name
from .utils import AttrGetter, format_docstring


CategoryActionLog = namedtuple('CategoryActionLog',
                               ('category', 'column_names', 'items'))
ActionLogItem = namedtuple('ActionLogItem', ('data', 'timestamp'))
ActionTableItem = namedtuple('ActionTableItem', ('column_names', 'converter'))


class Unchained:
    def __init__(self, app_config_cls: Optional[Type[AppConfig]] = None):
        self.app_config_cls = app_config_cls
        self._bundle_stores = {}
        self._shell_ctx = {}
        self._initialized = False

        self._services_registry = {}
        self._services = {}
        self.services = AttrGetter(self._services)

        self._extensions = {}
        self.extensions = AttrGetter(self._extensions)

        self._action_log = defaultdict(list)
        self._action_tables = {}

        self.register_action_table(
            'flask',
            ['app_name', 'kwargs'],
            lambda d: [d['app_name'], d['kwargs']])

        self.register_action_table(
            'bundle',
            ['name', 'location'],
            lambda bundle: [bundle.name,
                            f'{bundle.__module__}:{bundle.__name__}'])

        self.register_action_table(
            'hook',
            ['Priority', 'Name', 'Default Bundle Module',
             'Bundle Module Override Attr', 'Description'],
            lambda hook: [hook.priority,
                          hook.name,
                          hook.bundle_module_name or '',
                          hook.bundle_override_module_name_attr or '',
                          format_docstring(hook.__doc__)])

    def init_app(self,
                 app: Flask,
                 app_config_cls: Optional[Type[AppConfig]] = None,
                 bundles: Optional[List[Type[Bundle]]] = None,
                 ) -> None:
        self.app_config_cls = app_config_cls or self.app_config_cls
        app.extensions['unchained'] = self
        app.unchained = self

        # must import the RunHooksHook here to prevent a circular dependency
        from .hooks.run_hooks_hook import RunHooksHook
        RunHooksHook(self).run_hook(app, bundles or [])

    def service(self, name=None):
        """
        decorator to mark something as a service
        """
        if self._initialized:
            from warnings import warn
            warn('Services have already been initialized. Please register '
                 f'{name} sooner.')
            return lambda x: x

        def wrapper(service):
            self.register(name, service)
            return service
        return wrapper

    def register(self, name, service):
        """
        method to register a service
        """
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
            @wraps(fn)
            def decorator(*fn_args, **fn_kwargs):
                param_names = (args if has_explicit_args
                               else inspect.signature(fn).parameters)

                # FIXME: is it possible to not set kwargs when fn_args are
                # FIXME: explicitly set? (ie manual instantiation of services)
                for param_name in param_names:
                    if param_name in self._extensions:
                        fn_kwargs[param_name] = self._extensions[param_name]
                    elif param_name in self._services:
                        fn_kwargs[param_name] = self._services[param_name]
                return fn(*fn_args, **fn_kwargs)
            return decorator

        if used_without_parenthesis:
            return wrapper(args[0])
        return wrapper

    def log_action(self, category: str, data):
        converter = lambda x: x
        if category in self._action_tables:
            converter = self._action_tables[category].converter
        self._action_log[category].append((converter(data), datetime.now()))

    def register_action_table(self, category: str, columns, converter):
        self._action_tables[category] = ActionTableItem(columns, converter)

    def get_action_log(self, category: str):
        return CategoryActionLog(
            category,
            self._action_tables[category].column_names,
            self._action_log_items_by_category(category))

    def _action_log_items_by_category(self, category: str):
        items = [ActionLogItem(data, timestamp)
                 for data, timestamp in self._action_log[category]]
        return sorted(items, key=lambda row: row.timestamp)

    def _init_services(self):
        dag = nx.DiGraph()
        for name, service in self._services_registry.items():
            if not callable(service):
                self._services[name] = service
                continue

            dag.add_node(name)
            for param_name in inspect.signature(service).parameters:
                if param_name in self._services_registry:
                    dag.add_edge(name, param_name)

        try:
            instantiation_order = reversed(list(nx.topological_sort(dag)))
        except nx.NetworkXUnfeasible:
            msg = 'Circular dependency detected between services'
            problem_graph = ', '.join([f'{a} -> {b}'
                                       for a, b in nx.find_cycle(dag)])
            raise Exception(f'{msg}: {problem_graph}')

        for name in instantiation_order:
            service = self._services_registry[name]
            params = {n: self._services[n] for n in dag.successors(name)}

            if not inspect.isclass(service):
                self._services[name] = partial(service, **params)
            else:
                try:
                    self._services[name] = service(**params)
                except TypeError as e:
                    missing = str(e).rsplit(': ')[-1]
                    requester = f'{service.__module__}.{service.__name__}'
                    raise Exception(f'No service found with the name {missing} '
                                    f'(required by {requester})')

        self._initialized = True

    def __getattr__(self, name: str):
        if name in self._bundle_stores:
            return self._bundle_stores[name]
        raise AttributeError(name)


unchained = Unchained()
