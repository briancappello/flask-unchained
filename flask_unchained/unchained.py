import functools
import inspect
import itertools
import jinja2
import markupsafe
import networkx as nx

from flask import Flask, current_app
from py_meta_utils import _missing
from typing import *

from ._compat import QUART_ENABLED, LocalProxy
from .constants import (DEV, PROD, STAGING, TEST,
                        _DI_AUTOMATICALLY_HANDLED, _INJECT_CLS_ATTRS)
from .di import _ensure_service_name, _get_injected_value, injectable, _inject_cls_attrs
from .exceptions import ServiceUsageError
from .utils import AttrDict


class DeferredBundleBlueprintFunctions:
    """
    The public interface for replacing Blueprints with Bundles. Must be accessed
    via the :class:`flask_unchained.Unchained` extension instance, eg::

       from flask_unchained import Bundle, unchained

       class Foobar(Bundle):
           name = 'the_bundle_name'

       unchained.the_bundle_name.before_request()  # or any other public method on this class
    """

    def __init__(self):
        self._deferred_functions = []

    def _defer(self, fn):
        self._deferred_functions.append(fn)

    def before_request(self, fn=None):
        """
        Like :meth:`flask.Blueprint.before_request` but for a bundle. This function
        is only executed before each request that is handled by a view function
        of that bundle.
        """
        if fn is None:
            return self.before_request

        self._defer(lambda bp: bp.before_request(fn))
        return fn

    def after_request(self, fn=None):
        """
        Like :meth:`flask.Blueprint.after_request` but for a bundle. This function
        is only executed after each request that is handled by a function of
        that bundle.
        """
        if fn is None:
            return self.after_request

        self._defer(lambda bp: bp.after_request(fn))
        return fn

    def teardown_request(self, fn=None):
        """
        Like :meth:`flask.Blueprint.teardown_request` but for a bundle. This
        function is only executed when tearing down requests handled by a
        function of that bundle.  Teardown request functions are executed
        when the request context is popped, even when no actual request was
        performed.
        """
        if fn is None:
            return self.teardown_request

        self._defer(lambda bp: bp.teardown_request(fn))
        return fn

    def context_processor(self, fn=None):
        """
        Like :meth:`flask.Blueprint.context_processor` but for a bundle. This
        function is only executed for requests handled by a bundle.
        """
        if fn is None:
            return self.context_processor

        self._defer(lambda bp: bp.context_processor(fn))
        return fn

    def url_defaults(self, fn=None):
        """
        Callback function for URL defaults for this bundle. It's called
        with the endpoint and values and should update the values passed
        in place.
        """
        if fn is None:
            return self.url_defaults

        self._defer(lambda bp: bp.url_defaults(fn))
        return fn

    def url_value_preprocessor(self, fn=None):
        """
        Registers a function as URL value preprocessor for this
        bundle. It's called before the view functions are called and
        can modify the url values provided.
        """
        if fn is None:
            return self.url_value_preprocessor

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

        Otherwise works as the :meth:`flask.Blueprint.errorhandler` decorator.
        """
        def decorator(fn):
            self._defer(lambda bp: bp.register_error_handler(code_or_exception, fn))
            return fn
        return decorator

    if QUART_ENABLED:
        def before_websocket(self, fn=None):
            if fn is None:
                return self.before_websocket

            self._defer(lambda bp: bp.before_websocket(fn))
            return fn

        def after_websocket(self, fn=None):
            if fn is None:
                return self.after_websocket

            self._defer(lambda bp: bp.after_websocket(fn))
            return fn

        def teardown_websocket(self, fn=None):
            if fn is None:
                return self.teardown_websocket

            self._defer(lambda bp: bp.teardown_websocket(fn))
            return fn

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Probably you're trying to call a method at import "
                                  "time on the Unchained extension that doesn't exist?")


class _DeferredBundleBlueprintFunctionsStore:
    """
    An intermediary store that lives on :class:`~flask_unchained.Unchained` to
    return an instance of :class:`~flask_unchained.DeferredBundleBlueprintFunctions`
    for each bundle name lookup on us (implements a dict-like readonly interface).
    """
    def __init__(self):
        self._bundles = {}

    def __getitem__(self, bundle_name):
        if bundle_name not in self._bundles:
            self._bundles[bundle_name] = DeferredBundleBlueprintFunctions()
        return self._bundles[bundle_name]


class Unchained:
    """
    The ``Unchained`` extension. Responsible for initializing the app by loading all
    the things from bundles, keeping references to all of the various discovered
    bundles and things inside them, and for doing dependency injection. To get access
    to the ``unchained`` extension instance::

        from flask_unchained import unchained

    Also acts as a replacement for some of the public API of :class:`flask.Flask`.
    (The part that allows registering url rules, functions to run for handling errors,
    functions to run during the normal request response cycle, and methods for setting
    up the Jinja templating environment.)
    """

    def __init__(self, env: Optional[Union[DEV, PROD, STAGING, TEST]] = None):
        self.bundles = AttrDict()
        self._deferred_bundle_functions = _DeferredBundleBlueprintFunctionsStore()
        self.babel_bundle = None
        self.env = env
        self.extensions = AttrDict()
        self.services = AttrDict()

        self._app = None
        self._app_bundle_cls = None
        self._deferred_functions = []
        self._initialized = False
        self._models_initialized = False
        self._services_initialized = False
        self._services_registry = {}
        self._shell_ctx = {}

    def init_app(self,
                 app: Flask,
                 bundles: Optional[List] = None,  # FIXME Optional[List[Bundle]] on 3.7+
                 unchained_config: Optional[Dict[str, Any]] = None,
                 ) -> None:
        # deferred import to prevent circular dependency
        from .hooks.run_hooks_hook import RunHooksHook

        self.env = app.env or self.env
        app.extensions['unchained'] = self
        app.unchained = self
        self._app = app

        bundles = bundles or []
        for bundle in bundles:
            bundle._deferred_functions = \
                self._deferred_bundle_functions[bundle.name]._deferred_functions
        self.bundles = AttrDict({b.name: b for b in bundles})
        self.babel_bundle = self.bundles.get('babel_bundle', None)

        self._shell_ctx = {b.name: b for b in bundles}
        self._shell_ctx['unchained'] = self
        app.shell_context_processor(lambda: self._shell_ctx)

        for deferred in self._deferred_functions:
            deferred(app)

        run_hooks_hook = RunHooksHook(self)
        run_hooks_hook.run_hook(app, bundles, unchained_config)

        self._initialized = True

    def get_local_proxy(self, name):
        """
        Returns a :class:`~werkzeug.local.LocalProxy` to the extension or service
        with ``name`` as registered with the current app.
        """
        def get_extension_or_service_by_name():
            value = _get_injected_value(current_app.unchained, name, throw=False)
            if value is _missing:
                raise KeyError(f'No extension or service was found with the name {name}.')
            return value

        return LocalProxy(get_extension_or_service_by_name)

    def service(self, name: str = None):
        """
        Decorator to mark something as a service.
        """
        if self._services_initialized:
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
        if not isinstance(service, type):
            if hasattr(service, '__class__'):
                _ensure_service_name(service.__class__, name)
            self.services[name] = service
            return

        if self._services_initialized:
            from warnings import warn
            warn('Services have already been initialized. Please register '
                 f'{name} sooner.')
            return

        self._services_registry[_ensure_service_name(service, name)] = service

    def inject(self, *args):
        """
        Decorator to mark a class, method, or function as needing dependencies injected.

        Example usage::

            from flask_unchained import unchained, injectable

            # automatically figure out which params to inject
            @unchained.inject()
            def my_function(not_injected, some_service: SomeService = injectable):
                # do stuff

            # or declare injectables explicitly (makes the ``injectable`` default optional)
            @unchained.inject('some_service')
            def my_function(not_injected, some_service: SomeService):
                # do stuff

            # use it on a class to set up class attributes injection (and the constructor)
            @unchained.inject()
            class MyClass:
                some_service: SomeService = injectable

                def __init__(self, another_service: AnotherService = injectable):
                    self.another_service = another_service
        """
        used_without_parenthesis = len(args) and callable(args[0])
        has_explicit_args = len(args) and all(isinstance(x, str) for x in args)

        def wrapper(fn):
            cls = None
            if isinstance(fn, type):
                cls = fn
                fn = cls.__init__

            # check if the fn/class has already been wrapped with inject
            if hasattr(fn, '__signature__'):
                if not cls:
                    return fn
                if not hasattr(cls, '__signature__'):
                    # this happens when both the class and its __init__ method
                    # were decorated with @inject. which would be silly, but,
                    # it should still work regardless
                    cls.__signature__ = fn.__signature__
            if cls and hasattr(cls, '__di_name__'):
                return cls

            sig = inspect.signature(fn)

            # create a new function wrapping the original to inject params
            @functools.wraps(fn)
            def dependency_injector(*fn_args, **fn_kwargs):
                # figure out which params we need to inject (we don't want to
                # interfere with any params the user has passed manually)
                bound_args = sig.bind_partial(*fn_args, **fn_kwargs)
                required = set(sig.parameters.keys())
                have = set(bound_args.arguments.keys())
                need = required - have
                to_inject = need & (set(args) if has_explicit_args
                                    else {k for k, v in sig.parameters.items()
                                          if isinstance(v.default, str)
                                          and v.default == injectable})

                # try to inject needed params from extensions or services
                for param_name in to_inject:
                    try:
                        fn_kwargs[param_name] = _get_injected_value(
                            unchained_ext=self,
                            param_name=param_name,
                            requested_by=dependency_injector.__di_name__,
                        )
                    except:
                        continue

                # check to make sure we're not missing anything required
                # this check must live here so that it works when services get used
                # outside of flask unchained
                bound_args = sig.bind_partial(*fn_args, **fn_kwargs)
                bound_args.apply_defaults()
                for k, v in bound_args.arguments.items():
                    if isinstance(v, str) and v == injectable:
                        di_name = dependency_injector.__di_name__
                        is_constructor = ('.' not in di_name
                                          and di_name != di_name.lower())
                        action = 'initialized' if is_constructor else 'called'
                        raise ServiceUsageError(
                            f'{di_name} was {action} without the {k} parameter. '
                            f'Please supply it manually, or make sure it gets injected.'
                        )

                if cls and not getattr(cls, _DI_AUTOMATICALLY_HANDLED, False):
                    cls_attrs_to_inject = getattr(cls, _INJECT_CLS_ATTRS, [])
                    for attr, value in vars(cls).items():
                        if (isinstance(value, str)
                                and value == injectable
                                and attr not in cls_attrs_to_inject):
                            cls_attrs_to_inject.append(attr)

                    if has_explicit_args:
                        cls_attrs_to_inject = list(set(cls_attrs_to_inject) & set(args))
                    if cls_attrs_to_inject:
                        setattr(cls, _INJECT_CLS_ATTRS, cls_attrs_to_inject)
                        _inject_cls_attrs()(cls)

                return fn(*bound_args.args, **bound_args.kwargs)

            dependency_injector.__signature__ = sig
            dependency_injector.__di_name__ = getattr(fn, '__di_name__', fn.__name__)

            if cls:
                cls.__init__ = dependency_injector
                cls.__signature__ = sig
                return cls
            return dependency_injector

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
            for param_name in itertools.chain.from_iterable([
                inspect.signature(service).parameters,
                getattr(service, _INJECT_CLS_ATTRS)
            ]):
                if (param_name in self.services
                        or param_name in self.extensions
                        or param_name in self._services_registry):
                    dag.add_edge(name, param_name)

        try:
            instantiation_order = reversed(list(nx.topological_sort(dag)))
        except nx.NetworkXUnfeasible:
            msg = 'Circular dependency detected between services'
            problem_graph = ', '.join(f'{a} -> {b}'
                                      for a, b in nx.find_cycle(dag))
            raise Exception(f'{msg}: {problem_graph}')

        for name in instantiation_order:
            if name in self.services or name in self.extensions:
                continue

            service = self._services_registry[name]
            params = {n: self.extensions.get(n, self.services.get(n))
                      for n in dag.successors(name)
                      if n not in getattr(service, _INJECT_CLS_ATTRS)
                      and (n in self.extensions or n in self.services)}
            if 'config' in inspect.signature(service).parameters:
                params['config'] = self._app.config

            if not isinstance(service, type):
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

        self._services_initialized = True

    def __getattr__(self, name: str):
        """
        Implemented to allow accessing bundles by their name as attributes on the
        ``unchained`` extension instance.

        *Before* the app has been initialized (ie at import time), we don't
        actually know what bundles the user has configured, and therefore we
        need to make a compromise: *any* unrecognized attribute access before
        the app has been initialized is assumed to be a valid bundle name, and
        so we return a :class:`~flask_unchained.bundle.DeferredBundleBlueprintFunctions`
        instance that allows registering deferred functions (as a replacement
        for that part of the public Blueprint API).

        *After* the app has been initialized, we know what bundles the user
        configured, and can therefore return the correct bundle instance (or
        raise ``AttributeError`` if an invalid attribute was requested).
        """
        if name in self.bundles:
            return self.bundles[name]
        elif not self._initialized:
            return self._deferred_bundle_functions[name]
        raise AttributeError(name)

    def _defer(self, fn):
        if self._initialized:
            from warnings import warn
            warn('The app has already been initialized. '
                 f'Please register {fn.__name__} sooner.')
            return
        self._deferred_functions.append(fn)

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        """
        Register a new url rule. Acts the same as :meth:`flask.Flask.add_url_rule`.
        """
        self._defer(lambda app: app.add_url_rule(rule,
                                                 endpoint=endpoint,
                                                 view_func=view_func,
                                                 **options))

    def before_request(self, fn=None):
        """
        Registers a function to run before each request.

        For example, this can be used to open a database connection, or to load
        the logged in user from the session.

        The function will be called without any arguments. If it returns a
        non-None value, the value is handled as if it was the return value from
        the view, and further request handling is stopped.
        """
        if fn is None:
            return self.before_request

        self._defer(lambda app: app.before_request(fn))
        return fn

    def before_first_request(self, fn=None):
        """
        Registers a function to be run before the first request to this
        instance of the application.

        The function will be called without any arguments and its return
        value is ignored.
        """
        if fn is None:
            return self.before_first_request

        self._defer(lambda app: app.before_first_request(fn))
        return fn

    def after_request(self, fn=None):
        """
        Register a function to be run after each request.

        Your function must take one parameter, an instance of
        :attr:`response_class` and return a new response object or the
        same (see :meth:`process_response`).

        As of Flask 0.7 this function might not be executed at the end of the
        request in case an unhandled exception occurred.
        """
        if fn is None:
            return self.after_request

        self._defer(lambda app: app.after_request(fn))
        return fn

    def teardown_request(self, fn=None):
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
        if fn is None:
            return self.teardown_request

        self._defer(lambda app: app.teardown_request(fn))
        return fn

    def teardown_appcontext(self, fn=None):
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
        if fn is None:
            return self.teardown_appcontext

        self._defer(lambda app: app.teardown_appcontext(fn))
        return fn

    def context_processor(self, fn=None):
        """
        Registers a template context processor function.
        """
        if fn is None:
            return self.context_processor

        self._defer(lambda app: app.context_processor(fn))
        return fn

    def shell_context_processor(self, fn=None):
        """
        Registers a shell context processor function.
        """
        if fn is None:
            return self.shell_context_processor

        self._defer(lambda app: app.shell_context_processor(fn))
        return fn

    def url_value_preprocessor(self, fn=None):
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
        if fn is None:
            return self.url_value_preprocessor

        self._defer(lambda app: app.url_value_preprocessor(fn))
        return fn

    def url_defaults(self, fn=None):
        """
        Callback function for URL defaults for all view functions of the
        application.  It's called with the endpoint and values and should
        update the values passed in place.
        """
        if fn is None:
            return self.url_defaults

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
        Decorator to mark a function as a Jinja template filter.

        :param name: The name of the filter, if different from the function name.
        :param pass_context: Whether or not to pass the template context into the filter.
            If ``True``, the first argument must be the context.
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
        Decorator to mark a function as a Jinja template global (tag).

        :param name: The name of the tag, if different from the function name.
        :param pass_context: Whether or not to pass the template context into the tag.
            If ``True``, the first argument must be the context.
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
            If ``True``, the first argument must be the context.
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
        Decorator to mark a function as a Jinja template test.

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

    def _reset(self):
        """
        This method is for use by tests only!
        """
        self.bundles = AttrDict()
        self._deferred_bundle_functions = _DeferredBundleBlueprintFunctionsStore()
        self.babel_bundle = None
        self.env = None
        self.extensions = AttrDict()
        self.services = AttrDict()

        self._deferred_functions = []
        self._initialized = False
        self._models_initialized = False
        self._services_initialized = False
        self._services_registry = {}
        self._shell_ctx = {}

    if QUART_ENABLED:
        def add_websocket(
            self,
            path: str,
            endpoint: Optional[str] = None,
            view_func: Optional[Callable] = None,
            defaults: Optional[dict] = None,
            host: Optional[str] = None,
            subdomain: Optional[str] = None,
            *,
            strict_slashes: Optional[bool] = None,
        ):
            self._defer(lambda app: app.add_websocket(
                path,
                endpoint=endpoint,
                view_func=view_func,
                defaults=defaults,
                host=host,
                subdomain=subdomain,
                strict_slashes=strict_slashes,
            ))

        def before_serving(self, fn=None):
            if fn is None:
                return self.before_serving

            self._defer(lambda app: app.before_serving(fn))
            return fn

        def after_serving(self, fn=None):
            if fn is None:
                return self.after_serving

            self._defer(lambda app: app.after_serving(fn))
            return fn

        def before_websocket(self, fn=None):
            """Add a before websocket function.

            This is designed to be used as a decorator, if used to
            decorate a synchronous function, the function will be wrapped
            in :func:`~quart.utils.run_sync` and run in a thread executor
            (with the wrapped function returned). An example usage,

            .. code-block:: python

                @app.before_websocket
                async def func():
                    ...

            :param fn: The before websocket function itself.
            """
            if fn is None:
                return self.before_websocket

            self._defer(lambda app: app.before_websocket(fn))
            return fn

        def after_websocket(self, fn=None):
            if fn is None:
                return self.after_websocket

            self._defer(lambda app: app.after_websocket(fn))
            return fn

        def teardown_websocket(self, fn=None):
            if fn is None:
                return self.teardown_websocket

            self._defer(lambda app: app.teardown_websocket(fn))
            return fn


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


__all__ = [
    'unchained',
    'Unchained',
]
