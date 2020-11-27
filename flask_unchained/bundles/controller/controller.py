import copy
import functools
import os

from http import HTTPStatus
from types import FunctionType
from typing import *

from flask_unchained._compat import QUART_ENABLED
if QUART_ENABLED:
    from quart import (after_this_request, current_app as app, flash, jsonify,
                       make_response, render_template, render_template_string, request)
else:
    from flask import (after_this_request, current_app as app, flash, jsonify,
                       make_response, render_template, render_template_string, request)

from flask_unchained.di import _set_up_class_dependency_injection
from py_meta_utils import (AbstractMetaOption as _ControllerAbstractMetaOption,
                           McsArgs, MetaOption, MetaOptionsFactory, deep_getattr,
                           _missing, process_factory_meta_options)

from ...string_utils import snake_case
from .attr_constants import (
    CONTROLLER_ROUTES_ATTR, FN_ROUTES_ATTR, NO_ROUTES_ATTR,
    NOT_VIEWS_ATTR, REMOVE_SUFFIXES_ATTR)
from .utils import controller_name, redirect
from .route import Route


CONTROLLER_REMOVE_EXTRA_SUFFIXES = ['View']


def _get_not_views(clsdict, bases):
    not_views = deep_getattr({}, bases, NOT_VIEWS_ATTR, [])
    return ({name for name, method in clsdict.items()
             if _is_view_func(name, method)
             and not getattr(method, FN_ROUTES_ATTR, None)}.union(not_views))


def _get_remove_suffixes(name, bases, extras):
    existing_suffixes = deep_getattr({}, bases, REMOVE_SUFFIXES_ATTR, [])
    new_suffixes = [name] + extras
    return ([suffix for suffix in new_suffixes
             if suffix not in existing_suffixes] + existing_suffixes)


def _is_view_func(method_name, method):
    is_function = isinstance(method, FunctionType)
    is_private = method_name.startswith('_')
    has_no_routes = getattr(method, NO_ROUTES_ATTR, False)
    return is_function and not (is_private or has_no_routes)


class ControllerMetaclass(type):
    """
    Metaclass for Controller class

    Sets up automatic dependency injection and routes:
    - if base class, remember utility methods (NOT_VIEWS_ATTR)
    - if subclass of a base class, init CONTROLLER_ROUTES_ATTR by
      checking if methods were decorated with @route, otherwise
      create a new Route for each method that needs one
    """
    def __new__(mcs, name, bases, clsdict):
        clsdict['_view_funcs'] = {}
        mcs_args = McsArgs(mcs, name, bases, clsdict)
        _set_up_class_dependency_injection(mcs_args)
        if mcs_args.is_abstract:
            mcs_args.clsdict[REMOVE_SUFFIXES_ATTR] = _get_remove_suffixes(
                    name, bases, CONTROLLER_REMOVE_EXTRA_SUFFIXES)
            mcs_args.clsdict[NOT_VIEWS_ATTR] = _get_not_views(clsdict, bases)

        process_factory_meta_options(
            mcs_args, default_factory_class=ControllerMetaOptionsFactory)

        cls = super().__new__(*mcs_args)
        if mcs_args.is_abstract:
            return cls

        controller_routes: Dict[str, List[Route]] = copy.deepcopy(
            getattr(cls, CONTROLLER_ROUTES_ATTR, {})
        )
        not_views = deep_getattr({}, bases, NOT_VIEWS_ATTR)

        for method_name, method in clsdict.items():
            if (method_name in not_views
                    or not _is_view_func(method_name, method)):
                controller_routes.pop(method_name, None)
                continue

            controller_routes[method_name] = getattr(method, FN_ROUTES_ATTR,
                                                     [Route(None, method)])

        setattr(cls, CONTROLLER_ROUTES_ATTR, controller_routes)
        return cls

    def __init__(cls, name, bases, clsdict):
        super().__init__(name, bases, clsdict)
        for routes in getattr(cls, CONTROLLER_ROUTES_ATTR, {}).values():
            for route in routes:
                route._controller_cls = cls


class ControllerDecoratorsMetaOption(MetaOption):
    """
    A list of decorators to apply to all views in this controller.
    """

    def __init__(self):
        super().__init__('decorators', default=None, inherit=True)

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        if not all(callable(x) for x in value):
            raise ValueError(
                f'The {self.name} meta option must be a list of callables.')


class ControllerTemplateFolderNameMetaOption(MetaOption):
    """
    The name of the folder containing the templates for this controller's views. Defaults
    to the class name, with the suffixes ``Controller`` or ``View`` stripped, stopping
    after the first one is found (if any). It then gets converted to snake-case.
    """
    def __init__(self):
        super().__init__('template_folder', default=_missing, inherit=False)

    def get_value(self, meta, base_classes_meta, mcs_args: McsArgs):
        value = super().get_value(meta, base_classes_meta, mcs_args)
        if value is not _missing:
            return value

        return controller_name(mcs_args.name, mcs_args.getattr(REMOVE_SUFFIXES_ATTR))

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        if not isinstance(value, str) or os.sep in value:
            raise ValueError(
                f'The {self.name} meta option must be a string and not a full path')


class ControllerTemplateFileExtensionMetaOption(MetaOption):
    """
    The filename extension to use for templates for this controller's views.
    Defaults to None. ``Controller.render`` will use the
    ``app.config.TEMPLATE_FILE_EXTENSION`` setting as the default when this
    returns None.
    """
    def __init__(self):
        super().__init__('template_file_extension', default=None, inherit=False)

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        if not isinstance(value, str):
            raise ValueError(f'The {self.name} meta option must be a string')

    # def get_value(...):
    # NOTE: the logic for returning app.config.TEMPLATE_FILE_EXTENSION must
    # live in Controller.render (because the app context must be available.
    # it isn't here, because metaclass code runs at import time)


class ControllerUrlPrefixMetaOption(MetaOption):
    """
    The url prefix to use for all routes from this controller. Defaults to None.
    """
    def __init__(self):
        super().__init__('url_prefix', default=None, inherit=False)

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        if not isinstance(value, str):
            raise ValueError(f'The {self.name} meta option must be a string')


class ControllerEndpointPrefixMetaOption(MetaOption):
    def __init__(self, name='endpoint_prefix', default=_missing, inherit=False):
        super().__init__(name=name, default=default, inherit=inherit)

    def check_value(self, value: Any, mcs_args: McsArgs):
        if not value:
            return

        if not isinstance(value, str):
            raise ValueError(f'The {self.name} meta option must be a string')

    def get_value(self, meta, base_classes_meta, mcs_args: McsArgs):
        value = super().get_value(meta, base_classes_meta, mcs_args)
        if value is not _missing:
            return value

        return snake_case(mcs_args.name)


class ControllerMetaOptionsFactory(MetaOptionsFactory):
    _options = [
        _ControllerAbstractMetaOption,
        ControllerDecoratorsMetaOption,
        ControllerTemplateFolderNameMetaOption,
        ControllerTemplateFileExtensionMetaOption,
        ControllerUrlPrefixMetaOption,
        ControllerEndpointPrefixMetaOption,
    ]


class Controller(metaclass=ControllerMetaclass):
    """
    Base class for views.

    Concrete controllers should subclass this and their public methods will used as
    the views. By default view methods will be assigned routing defaults with the
    HTTP method GET and paths as the kebab-cased method name. For example::

        from flask_unchained import Controller, injectable, route, no_route
        from flask_unchained.bundles.sqlalchemy import SessionManager

        class SiteController(Controller):
            class Meta:
                abstract = False  # this is the default; no need to set explicitly
                decorators = ()  # a list of decorators to apply to all view methods
                                 # on the controller (defaults to an empty tuple)
                template_folder = 'site'  # defaults to the snake_cased class name,
                                          # minus any Controller/View suffix
                template_file_extension = app.config.TEMPLATE_FILE_EXTENSION = '.html'
                url_prefix = None  # optional url prefix to use for all routes
                endpoint_prefix = 'site_controller'  # defaults to snake_cased class name

            # dependency injection works automatically on controllers
            session_manager: SessionManager = injectable

            @route('/')  # change the default path of '/index' to '/'
            def index():
                return self.render('index')  # site/index.html

            # use the defaults, equivalent to @route('/about-us', methods=['GET'])
            def about_us():
                return self.render('about_us.html')  # site/about_us.html

            # change the path, HTTP methods, and the endpoint
            @route('/contact', methods=['GET', 'POST'], endpoint='site_controller.contact')
            def contact_us():
                # ...
                return self.render('site/contact.html.j2')  # site/contact.html.j2

            @no_route
            def public_utility_method():
                return 'not a view'

            def _protected_utility_method():
                return 'not a view'

    How do the calls to render know which template to use? They look in
    ``Bundle.template_folder`` for a folder with the controller's
    ``Meta.template_folder`` and a file with the passed name and
    ``Meta.template_file_extension``. For example::

        class SiteController(Controller):
            # these defaults are automatically determined, unless you override them
            class Meta:
                template_folder = 'site'  # snake_cased class name (minus Controller suffix)
                template_file_extension = '.html'  # from Config.TEMPLATE_FILE_EXTENSION

            def about_us():
                return self.render('about_us')  # site/about_us.html

            def contact():
                return self.render('contact')  # site/contact.html

            def index():
                return self.render('index')  # site/index.html

        # your_bundle_root
        ├── __init__.py
        ├── templates
        │   └── site
        │       ├── about_us.html
        │       ├── contact.html
        │       └── index.html
        └── views
            └── site_controller.py
    """
    _meta_options_factory_class = ControllerMetaOptionsFactory

    # the metaclass ensures a unique _view_funcs dict for each subclass of controller
    _view_funcs: Dict[str, FunctionType] = {}  # keyed by method names on controllers

    class Meta:
        abstract = True

    def flash(self, msg: str, category: Optional[str] = None):
        """
        Convenience method for flashing messages.

        :param msg: The message to flash.
        :param category: The category of the message.
        """
        if not request.is_json and app.config.FLASH_MESSAGES:
            flash(msg, category)

    def render(self, template_name: str, **ctx):
        """
        Convenience method for rendering a template.

        :param template_name: The template's name. Can either be a full path,
                              or a filename in the controller's template folder.
                              (The file extension can be omitted.)
        :param ctx: Context variables to pass into the template.
        """
        if '.' not in template_name:
            template_file_extension = (self.Meta.template_file_extension
                                       or app.config.TEMPLATE_FILE_EXTENSION)
            template_name = f'{template_name}{template_file_extension}'
        if self.Meta.template_folder and os.sep not in template_name:
            template_name = os.path.join(self.Meta.template_folder,
                                         template_name)
        return render_template(template_name, **ctx)

    def render_template_string(self, source, **ctx):
        return render_template_string(source, **ctx)

    def redirect(self,
                 where: Optional[str] = None,
                 default: Optional[str] = None,
                 override: Optional[str] = None,
                 **url_kwargs):
        """
        Convenience method for returning redirect responses.

        :param where: A method name from this controller, a URL, an endpoint, or
                      a config key name to redirect to.
        :param default: A method name from this controller, a URL, an endpoint, or
                        a config key name to redirect to if ``where`` is invalid.
        :param override: Explicitly redirect to a method name from this controller,
                         a URL, an endpoint, or a config key name (takes precedence
                         over the ``next`` value in query strings or forms)
        :param url_kwargs: the variable arguments of the URL rule
        :param _anchor: if provided this is added as anchor to the URL.
        :param _external: if set to ``True``, an absolute URL is generated. Server
                          address can be changed via ``SERVER_NAME`` configuration
                          variable which defaults to `localhost`.
        :param _external_host: if specified, the host of an external server to
                               generate urls for (eg https://example.com or
                               localhost:8888)
        :param _method: if provided this explicitly specifies an HTTP method.
        :param _scheme: a string specifying the desired URL scheme. The `_external`
                        parameter must be set to ``True`` or a :exc:`ValueError`
                        is raised. The default behavior uses the same scheme as
                        the current request, or ``PREFERRED_URL_SCHEME`` from the
                        :ref:`app configuration <config>` if no request context is
                        available. As of Werkzeug 0.10, this also can be set
                        to an empty string to build protocol-relative URLs.
        """
        return redirect(where, default, override, _cls=self, **url_kwargs)

    def jsonify(self,
                data: Any,
                code: Union[int, Tuple[int, str, str]] = HTTPStatus.OK,
                headers: Optional[Dict[str, str]] = None,
                ):
        """
        Convenience method to return json responses.

        :param data: The python data to jsonify.
        :param code: The HTTP status code to return.
        :param headers: Any optional headers.
        """
        return jsonify(data), code, headers or {}

    def errors(self,
               errors: List[str],
               code: Union[int, Tuple[int, str, str]] = HTTPStatus.BAD_REQUEST,
               key: str = 'errors',
               headers: Optional[Dict[str, str]] = None,
               ):
        """
        Convenience method to return errors as json.

        :param errors: The list of errors.
        :param code: The HTTP status code.
        :param key: The key to return the errors under.
        :param headers: Any optional headers.
        """
        return jsonify({key: errors}), code, headers or {}

    def after_this_request(self, fn):
        """
        Register a function to run after this request.

        :param fn: The function to run. It should accept one argument, the
                   response, which it should also return
        """
        after_this_request(fn)

    def make_response(self, *args):
        return make_response(*args)

    ################################################
    # the remaining methods are internal/protected #
    ################################################

    @classmethod
    def method_as_view(cls, method_name, *class_args, **class_kwargs):
        # this code, combined with apply_decorators and dispatch_request, is
        # modified from Flask's View.as_view classmethod. Differences:
        #
        # - we pass method_name to dispatch_request, to allow for easier
        #   customization of behavior by subclasses
        # - we apply decorators later, so they get called when the view does
        # - we also apply decorators listed in Meta.decorators in reverse,
        #   so that they get applied in the logical top-to-bottom order as
        #   declared in controllers
        if method_name not in cls._view_funcs:
            if QUART_ENABLED:
                async def view_func(*args, **kwargs):
                    self = view_func.view_class(*class_args, **class_kwargs)
                    return await self.dispatch_request(method_name, *args, **kwargs)
            else:
                def view_func(*args, **kwargs):
                    self = view_func.view_class(*class_args, **class_kwargs)
                    return self.dispatch_request(method_name, *args, **kwargs)

            wrapper_assignments = set(functools.WRAPPER_ASSIGNMENTS) - {'__qualname__'}
            functools.update_wrapper(view_func, getattr(cls, method_name),
                                     assigned=list(wrapper_assignments))
            view_func.view_class = cls
            cls._view_funcs[method_name] = view_func

        return cls._view_funcs[method_name]

    def dispatch_request(self, method_name, *view_args, **view_kwargs):
        decorators = self.get_decorators(method_name)
        view_func = self.apply_decorators(view_func=getattr(self, method_name),
                                          decorators=decorators)
        return view_func(*view_args, **view_kwargs)

    def get_decorators(self, method_name):
        return self.Meta.decorators or ()

    def apply_decorators(self, view_func, decorators):
        if not decorators:
            return view_func

        original_view_func = view_func
        for decorator in reversed(decorators):
            view_func = decorator(view_func)
        return functools.wraps(original_view_func)(view_func)


__all__ = [
    'Controller',
    'ControllerMetaclass',
    'ControllerMetaOptionsFactory',
]
