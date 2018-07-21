import functools
import jinja2
import markupsafe

from collections import defaultdict, namedtuple
from datetime import datetime
from flask import Flask
from typing import *

from .bundle import Bundle
from .constants import DEV, PROD, STAGING, TEST
from .di import DependencyInjectionMixin
from .utils import format_docstring


CategoryActionLog = namedtuple('CategoryActionLog',
                               ('category', 'column_names', 'items'))
ActionLogItem = namedtuple('ActionLogItem', ('data', 'timestamp'))
ActionTableItem = namedtuple('ActionTableItem', ('column_names', 'converter'))


class Unchained(DependencyInjectionMixin):
    def __init__(self, env: Optional[Union[DEV, PROD, STAGING, TEST]] = None):
        super().__init__(env)

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
        # must import here to prevent circular import errors
        try:
            from .bundles.babel import BabelBundle
            self.babel_bundle = [b for b in bundles if issubclass(b, BabelBundle)][0]
        except IndexError:
            self.babel_bundle = None

        self.bundles = bundles
        self.env = env or self.env
        app.extensions['unchained'] = self
        app.unchained = self

        for deferred in self._deferred_functions:
            deferred(app)

        # must import the RunHooksHook here to prevent a circular dependency
        from .hooks.run_hooks_hook import RunHooksHook
        RunHooksHook(self).run_hook(app, bundles or [])
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
