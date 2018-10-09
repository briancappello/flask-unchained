import functools
import inspect
import jinja2
import markupsafe
import networkx as nx

from flask import Flask, current_app
from typing import *
from werkzeug.local import LocalProxy

from .constants import DEV, PROD, STAGING, TEST
from .di import ensure_service_name, injectable
from .exceptions import ServiceUsageError
from .utils import AttrDict


class _DeferredBundleFunctions:
    def __init__(self):
        self._deferred_functions = []

    def _defer(self, fn):
        self._deferred_functions.append(fn)

    def before_request(self, fn):
        """
        Like :meth:`~flask.Blueprint.before_request` but for a bundle. This function
        is only executed before each request that is handled by a view function
        of that bundle.
        """
        self._defer(lambda bp: bp.before_request(fn))

    def after_request(self, fn):
        """
        Like :meth:`~flask.Blueprint.after_request` but for a bundle. This function
        is only executed after each request that is handled by a function of
        that bundle.
        """
        self._defer(lambda bp: bp.after_request(fn))

    def teardown_request(self, fn):
        """
        Like :meth:`~flask.Blueprint.teardown_request` but for a bundle. This
        function is only executed when tearing down requests handled by a
        function of that bundle.  Teardown request functions are executed
        when the request context is popped, even when no actual request was
        performed.
        """
        self._defer(lambda bp: bp.teardown_request(fn))

    def context_processor(self, fn):
        """
        Like :meth:`~flask.Blueprint.context_processor` but for a bundle. This
        function is only executed for requests handled by a bundle.
        """
        self._defer(lambda bp: bp.context_processor(fn))
        return fn

    def url_defaults(self, fn):
        """
        Callback function for URL defaults for this bundle. It's called
        with the endpoint and values and should update the values passed
        in place.
        """
        self._defer(lambda bp: bp.url_defaults(fn))
        return fn

    def url_value_preprocessor(self, fn):
        """
        Registers a function as URL value preprocessor for this
        bundle. It's called before the view functions are called and
        can modify the url values provided.
        """
        self._defer(lambda bp: bp.url_value_preprocessor(fn))
        return fn

    def errorhandler(self, code_or_exception):
        """
        Registers an error handler that becomes active for this bundle
        only.  Please be aware that routing does not happen local to a
        bundle so an error handler for 404 usually is not handled by
        a bundle unless it is caused inside a view function.  Another
        special case is the 500 internal server error which is always looked
        up from the application.

        Otherwise works as the :meth:`~flask.Blueprint.errorhandler` decorator.
        """
        def decorator(fn):
            self._defer(lambda bp: bp.register_error_handler(code_or_exception, fn))
            return fn
        return decorator


class _DeferredBundleFunctionsStore:
    def __init__(self):
        self._bundles = {}

    def __getitem__(self, bundle_name):
        if bundle_name not in self._bundles:
            self._bundles[bundle_name] = _DeferredBundleFunctions()
        return self._bundles[bundle_name]


class Unchained:
    """
    The `Unchained` extension. Responsible for loading bundles, keeping references
    to all of the various discovered bundles and classes, and for doing dependency
    injection::

        from flask_unchained import unchained
    """

    def __init__(self, env: Optional[Union[DEV, PROD, STAGING, TEST]] = None):
        self.bundles = AttrDict()
        self._bundles = _DeferredBundleFunctionsStore()
        self.app_bundle = None
        self.babel_bundle = None
        self.env = env
        self.extensions = AttrDict()
        self.services = AttrDict()

        self._deferred_functions = []
        self._initialized = False
        self._services_registry = {}
        self._shell_ctx = {}

    def init_app(self,
                 app: Flask,
                 env: Optional[Union[DEV, PROD, STAGING, TEST]] = None,

                 # FIXME: properly type hint this once on 3.7+, on 3.6 we get
                 # circular import errors
                 bundles: Optional[List] = None,
                 _config_overrides: Optional[Dict[str, Any]] = None,
                 ) -> None:
        bundles = bundles or []
        for b in bundles:
            b._deferred_functions = self._bundles[b.name]._deferred_functions
        self.bundles = AttrDict({b.name: b for b in bundles})
        app.shell_context_processor(lambda: {b.__class__.__name__: b for b in bundles})

        try:
            # must import AppBundle here to prevent circular dependency
            from .bundle import AppBundle
            self.app_bundle = [b for b in bundles if isinstance(b, AppBundle)][0]
        except IndexError:
            self.app_bundle = None

        try:
            # must import BabelBundle here to prevent circular dependency
            from .bundles.babel import BabelBundle
            self.babel_bundle = [b for b in bundles if isinstance(b, BabelBundle)][0]
        except IndexError:
            self.babel_bundle = None

        self.env = env or self.env
        app.env = self.env

        app.extensions['unchained'] = self
        app.unchained = self

        for deferred in self._deferred_functions:
            deferred(app)

        # must import the RunHooksHook here to prevent a circular dependency
        from .hooks.run_hooks_hook import RunHooksHook
        run_hooks_hook = RunHooksHook(self)
        run_hooks_hook.run_hook(app, bundles, _config_overrides=_config_overrides)
        self._initialized = True

    def get_extension_local_proxy(self, ext_name):
        """
        Returns a :class:`~werkzeug.local.LocalProxy` to the extension with
        `ext_name` as registered with the current app.
        """
        return LocalProxy(lambda: current_app.unchained.extensions[ext_name])

    def get_service_local_proxy(self, service_name):
        """
        Returns a :class:`~werkzeug.local.LocalProxy` to the service with
        `service_name` as registered with the current app.
        """
        return LocalProxy(lambda: current_app.unchained.services[service_name])

    def _reset(self):
        """
        This method is for use by tests only!
        """
        self._initialized = False
        self._services_registry = {}
        self.extensions = AttrDict()
        self.services = AttrDict()

    def service(self, name: str = None):
        """
        Decorator to mark something as a service.
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
        Method to register a service.
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
        Decorator to mark a callable as needing dependencies injected.
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

    def _defer(self, fn):
        if self._initialized:
            from warnings import warn
            warn('The app has already been initialized. Please register '
                 f'{fn.__name__} sooner.')
        self._deferred_functions.append(fn)

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        """
        Register a new url rule. Acts the same as :meth:`~flask.Flask.add_url_rule`.
        """
        self._defer(lambda app: app.add_url_rule(rule,
                                                 endpoint=endpoint,
                                                 view_func=view_func,
                                                 **options))

    def before_request(self, fn):
        """
        Registers a function to run before each request.

        For example, this can be used to open a database connection, or to load
        the logged in user from the session.

        The function will be called without any arguments. If it returns a
        non-None value, the value is handled as if it was the return value from
        the view, and further request handling is stopped.
        """
        self._defer(lambda app: app.before_request(fn))
        return fn

    def before_first_request(self, fn):
        """
        Registers a function to be run before the first request to this
        instance of the application.

        The function will be called without any arguments and its return
        value is ignored.
        """
        self._defer(lambda app: app.before_first_request(fn))
        return fn

    def after_request(self, fn):
        """
        Register a function to be run after each request.

        Your function must take one parameter, an instance of
        :attr:`response_class` and return a new response object or the
        same (see :meth:`process_response`).

        As of Flask 0.7 this function might not be executed at the end of the
        request in case an unhandled exception occurred.
        """
        self._defer(lambda app: app.after_request(fn))
        return fn

    def teardown_request(self, fn):
        """
        Register a function to be run at the end of each request,
        regardless of whether there was an exception or not.  These functions
        are executed when the request context is popped, even if not an
        actual request was performed.

        Example::

            ctx = app.test_request_context()
            ctx.push()
            ...
            ctx.pop()

        When ``ctx.pop()`` is executed in the above example, the teardown
        functions are called just before the request context moves from the
        stack of active contexts.  This becomes relevant if you are using
        such constructs in tests.

        Generally teardown functions must take every necessary step to avoid
        that they will fail.  If they do execute code that might fail they
        will have to surround the execution of these code by try/except
        statements and log occurring errors.

        When a teardown function was called because of an exception it will
        be passed an error object.

        The return values of teardown functions are ignored.

        .. admonition:: Debug Note

           In debug mode Flask will not tear down a request on an exception
           immediately.  Instead it will keep it alive so that the interactive
           debugger can still access it.  This behavior can be controlled
           by the ``PRESERVE_CONTEXT_ON_EXCEPTION`` configuration variable.
        """
        self._defer(lambda app: app.teardown_request(fn))
        return fn

    def teardown_appcontext(self, fn):
        """
        Registers a function to be called when the application context
        ends.  These functions are typically also called when the request
        context is popped.

        Example::

            ctx = app.app_context()
            ctx.push()
            ...
            ctx.pop()

        When ``ctx.pop()`` is executed in the above example, the teardown
        functions are called just before the app context moves from the
        stack of active contexts.  This becomes relevant if you are using
        such constructs in tests.

        Since a request context typically also manages an application
        context it would also be called when you pop a request context.

        When a teardown function was called because of an unhandled exception
        it will be passed an error object. If an :meth:`errorhandler` is
        registered, it will handle the exception and the teardown will not
        receive it.

        The return values of teardown functions are ignored.
        """
        self._defer(lambda app: app.teardown_appcontext(fn))
        return fn

    def context_processor(self, fn):
        """
        Registers a template context processor function.
        """
        self._defer(lambda app: app.context_processor(fn))
        return fn

    def shell_context_processor(self, fn):
        """
        Registers a shell context processor function.
        """
        self._defer(lambda app: app.shell_context_processor(fn))
        return fn

    def url_value_preprocessor(self, fn):
        """
        Register a URL value preprocessor function for all view
        functions in the application. These functions will be called before the
        :meth:`before_request` functions.

        The function can modify the values captured from the matched url before
        they are passed to the view. For example, this can be used to pop a
        common language code value and place it in ``g`` rather than pass it to
        every view.

        The function is passed the endpoint name and values dict. The return
        value is ignored.
        """
        self._defer(lambda app: app.url_value_preprocessor(fn))
        return fn

    def url_defaults(self, fn):
        """
        Callback function for URL defaults for all view functions of the
        application.  It's called with the endpoint and values and should
        update the values passed in place.
        """
        self._defer(lambda app: app.url_defaults(fn))
        return fn

    def errorhandler(self, code_or_exception):
        """
        Register a function to handle errors by code or exception class.

        A decorator that is used to register a function given an
        error code.  Example::

            @app.errorhandler(404)
            def page_not_found(error):
                return 'This page does not exist', 404

        You can also register handlers for arbitrary exceptions::

            @app.errorhandler(DatabaseError)
            def special_exception_handler(error):
                return 'Database connection failed', 500

        :param code_or_exception: the code as integer for the handler, or
                                  an arbitrary exception
        """
        def decorator(fn):
            self._defer(lambda app: app.register_error_handler(code_or_exception, fn))
            return fn
        return decorator

    def template_filter(self,
                        arg: Optional[Callable] = None,
                        *,
                        name: Optional[str] = None,
                        pass_context: bool = False,
                        inject: Optional[Union[bool, Iterable[str]]] = None,
                        safe: bool = False,
                        ) -> Callable:
        """
        Decorator to mark a function as a jinja template filter.

        :param name: The name of the filter, if different from the function name.
        :param pass_context: Whether or not to pass the template context into the filter.
            If true, the first argument must be the context.
        :param inject: Whether or not this filter needs any dependencies injected.
        :param safe: Whether or not to mark the output of this filter as html-safe.
        """
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

    def template_global(self,
                        arg: Optional[Callable] = None,
                        *,
                        name: Optional[str] = None,
                        pass_context: bool = False,
                        inject: Optional[Union[bool, Iterable[str]]] = None,
                        safe: bool = False,
                        ) -> Callable:
        """
        Decorator to mark a function as a jinja template global (tag).

        :param name: The name of the tag, if different from the function name.
        :param pass_context: Whether or not to pass the template context into the tag.
            If true, the first argument must be the context.
        :param inject: Whether or not this tag needs any dependencies injected.
        :param safe: Whether or not to mark the output of this tag as html-safe.
        """
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

    def template_tag(self,
                     arg: Optional[Callable] = None,
                     *,
                     name: Optional[str] = None,
                     pass_context: bool = False,
                     inject: Optional[Union[bool, Iterable[str]]] = None,
                     safe: bool = False,
                     ) -> Callable:
        """
        Alias for :meth:`template_global`.

        :param name: The name of the tag, if different from the function name.
        :param pass_context: Whether or not to pass the template context into the tag.
            If true, the first argument must be the context.
        :param inject: Whether or not this tag needs any dependencies injected.
        :param safe: Whether or not to mark the output of this tag as html-safe.
        """
        return self.template_global(arg, name=name, pass_context=pass_context,
                                    inject=inject, safe=safe)

    def template_test(self,
                      arg: Optional[Callable] = None,
                      *,
                      name: Optional[str] = None,
                      inject: Optional[Union[bool, Iterable[str]]] = None,
                      safe: bool = False,
                      ) -> Callable:
        """
        Decorator to mark a function as a jinja template test.

        :param name: The name of the test, if different from the function name.
        :param inject: Whether or not this test needs any dependencies injected.
        :param safe: Whether or not to mark the output of this test as html-safe.
        """
        def wrapper(fn):
            fn = _inject(fn, inject)
            if safe:
                fn = _make_safe(fn)
            self._defer(lambda app: app.add_template_test(fn, name=name))
            return fn

        if callable(arg):
            return wrapper(arg)
        return wrapper

    def __getattr__(self, name: str):
        if name in self.bundles:
            return self.bundles[name]
        elif not self._initialized:
            return self._bundles[name]
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
