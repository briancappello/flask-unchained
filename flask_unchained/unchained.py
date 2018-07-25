import functools
import inspect
import jinja2
import markupsafe
import networkx as nx

from collections import defaultdict, namedtuple
from datetime import datetime
from flask import Flask
from typing import *

from .bundle import Bundle
from .constants import DEV, PROD, STAGING, TEST
from .di import ensure_service_name, injectable
from .exceptions import ServiceUsageError
from .utils import AttrDict, format_docstring


CategoryActionLog = namedtuple('CategoryActionLog',
                               ('category', 'column_names', 'items'))
ActionLogItem = namedtuple('ActionLogItem', ('data', 'timestamp'))
ActionTableItem = namedtuple('ActionTableItem', ('column_names', 'converter'))


class Unchained:
    def __init__(self, env: Optional[Union[DEV, PROD, STAGING, TEST]] = None):
        self._initialized = False
        self._services_registry = {}
        self.extensions = AttrDict()
        self.services = AttrDict()

        self.bundles = []
        self.babel_bundle = None
        self.env = env
        self._bundle_stores = {}
        self._shell_ctx = {}
        self._deferred_functions = []
        self._initialized = False

        self._action_log = defaultdict(list)
        self._action_tables = {}

        self.register_action_table(
            'flask',
            ['app_name', 'root_path', 'kwargs'],
            lambda d: [d['app_name'], d['root_path'], d['kwargs']])

        self.register_action_table(
            'bundle',
            ['name', 'location'],
            lambda bundle: [bundle.name,
                            f'{bundle.__module__}:{bundle.__name__}'])

        self.register_action_table(
            'hook',
            ['Hook Name', 'Default Bundle Module',
             'Bundle Module Override Attr', 'Description'],
            lambda hook: [hook.name,
                          hook.bundle_module_name or '',
                          hook.bundle_override_module_name_attr or '',
                          format_docstring(hook.__doc__)])

    def init_app(self,
                 app: Flask,
                 env: Optional[Union[DEV, PROD, STAGING, TEST]] = None,
                 bundles: Optional[List[Type[Bundle]]] = None,
                 ) -> None:
        self.bundles = bundles
        self.env = env or self.env
        app.extensions['unchained'] = self
        app.unchained = self
        app.shell_context_processor(lambda: {b.__name__: b for b in bundles})

        try:
            # must import BabelBundle here to prevent circular dependency
            from .bundles.babel import BabelBundle
            self.babel_bundle = [b for b in bundles if issubclass(b, BabelBundle)][0]
        except IndexError:
            self.babel_bundle = None

        for deferred in self._deferred_functions:
            deferred(app)

        # must import the RunHooksHook here to prevent a circular dependency
        from .hooks.run_hooks_hook import RunHooksHook
        RunHooksHook(self).run_hook(app, bundles or [])
        self._initialized = True

    def _reset(self):
        """
        this method is for testing only!
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

    def _defer(self, fn):
        if self._initialized:
            from warnings import warn
            warn('The app has already been initialized. Please register '
                 f'{fn.__name__} sooner.')
        self._deferred_functions.append(fn)

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        self._defer(lambda app: app.add_url_rule(rule,
                                                 endpoint=endpoint,
                                                 view_func=view_func,
                                                 **options))

    def before_request(self, fn):
        self._defer(lambda app: app.before_request(fn))
        return fn

    def before_first_request(self, fn):
        self._defer(lambda app: app.before_first_request(fn))
        return fn

    def after_request(self, fn):
        self._defer(lambda app: app.after_request(fn))
        return fn

    def teardown_request(self, fn):
        self._defer(lambda app: app.teardown_request(fn))
        return fn

    def teardown_appcontext(self, fn):
        self._defer(lambda app: app.teardown_appcontext(fn))
        return fn

    def context_processor(self, fn):
        self._defer(lambda app: app.context_processor(fn))
        return fn

    def shell_context_processor(self, fn):
        self._defer(lambda app: app.shell_context_processor(fn))
        return fn

    def url_value_preprocessor(self, fn):
        self._defer(lambda app: app.url_value_preprocessor(fn))
        return fn

    def url_defaults(self, fn):
        self._defer(lambda app: app.url_defaults(fn))
        return fn

    def errorhandler(self, code_or_exception):
        def decorator(fn):
            self._defer(lambda app: app.register_error_handler(code_or_exception, fn))
            return fn
        return decorator

    def template_filter(self, arg: Optional[Callable] = None,
                        *,
                        name: Optional[str] = None,
                        pass_context: bool = False,
                        inject: Optional[Union[bool, Iterable[str]]] = None,
                        safe: bool = False,
                        ) -> Callable:
        def wrapper(fn):
            fn = _inject(fn, inject)
            if safe:
                fn = _make_safe(fn)
            if pass_context:
                fn = jinja2.contextfilter(fn)
            self._defer(lambda app: app.add_template_filter(fn, name=name))
            return fn

        if callable(arg):
            return wrapper(arg)
        return wrapper

    def template_global(self, arg: Optional[Callable] = None,
                        *,
                        name: Optional[str] = None,
                        pass_context: bool = False,
                        inject: Optional[Union[bool, Iterable[str]]] = None,
                        safe: bool = False,
                        ) -> Callable:
        def wrapper(fn):
            fn = _inject(fn, inject)
            if safe:
                fn = _make_safe(fn)
            if pass_context:
                fn = jinja2.contextfunction(fn)
            self._defer(lambda app: app.add_template_global(fn, name=name))
            return fn

        if callable(arg):
            return wrapper(arg)
        return wrapper

    def template_tag(self, arg: Optional[Callable] = None,
                     *,
                     name: Optional[str] = None,
                     pass_context: bool = False,
                     inject: Optional[Union[bool, Iterable[str]]] = None,
                     safe: bool = False,
                     ) -> Callable:
        """
        alias for :meth:`template_global`
        """
        return self.template_global(arg, name=name, pass_context=pass_context,
                                    inject=inject, safe=safe)

    def template_test(self, arg: Optional[Callable] = None,
                      *,
                      name: Optional[str] = None,
                      inject: Optional[Union[bool, Iterable[str]]] = None,
                      safe: bool = False,
                      ) -> Callable:
        def wrapper(fn):
            fn = _inject(fn, inject)
            if safe:
                fn = _make_safe(fn)
            self._defer(lambda app: app.add_template_test(fn, name=name))
            return fn

        if callable(arg):
            return wrapper(arg)
        return wrapper

    def _action_log_items_by_category(self, category: str):
        items = [ActionLogItem(data, timestamp)
                 for data, timestamp in self._action_log[category]]
        return sorted(items, key=lambda row: row.timestamp)

    def __getattr__(self, name: str):
        if name in self._bundle_stores:
            return self._bundle_stores[name]
        raise AttributeError(name)


def _inject(fn, inject_args):
    if not inject_args:
        return fn

    inject_args = inject_args if isinstance(inject_args, Iterable) else []
    return unchained.inject(*inject_args)(fn)


def _make_safe(fn):
    @functools.wraps(fn)
    def safe_fn(*args, **kwargs):
        return markupsafe.Markup(fn(*args, **kwargs))
    return safe_fn


unchained = Unchained()
