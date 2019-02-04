import copy
import functools
import os

from flask import (after_this_request, current_app as app, flash, jsonify,
                   make_response, render_template, request)
from flask_unchained.di import _set_up_class_dependency_injection
from py_meta_utils import (AbstractMetaOption as _ControllerAbstractMetaOption,
                           McsArgs, MetaOption, MetaOptionsFactory, deep_getattr,
                           _missing, process_factory_meta_options)
from http import HTTPStatus
from types import FunctionType
from typing import *

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


class _ControllerMetaclass(type):
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
        if clsdict.get('__abstract__',
                       getattr(clsdict.get('Meta'), 'abstract', False)):
            mcs_args.clsdict[REMOVE_SUFFIXES_ATTR] = _get_remove_suffixes(
                    name, bases, CONTROLLER_REMOVE_EXTRA_SUFFIXES)
            mcs_args.clsdict[NOT_VIEWS_ATTR] = _get_not_views(clsdict, bases)

        process_factory_meta_options(
            mcs_args, default_factory_class=_ControllerMetaOptionsFactory)

        cls = super().__new__(*mcs_args)
        if mcs_args.Meta.abstract:
            return cls

        controller_routes = copy.deepcopy(getattr(cls, CONTROLLER_ROUTES_ATTR, {}))
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


class _ControllerDecoratorsMetaOption(MetaOption):
    """
    A list of decorators to apply to all views in this controller.
    """

    def __init__(self):
        super().__init__('decorators', default=None, inherit=True)

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        assert all(callable(x) for x in value), \
            f'The {self.name} meta option must be a list of callables.'


class _ControllerTemplateFolderNameMetaOption(MetaOption):
    """
    The name of the folder containing the templates for this controller's views. Defaults
    to the class name, with the suffixes ``Controller`` or ``View`` stripped, stopping
    after the first one is found (if any). It then gets pluralized and converted to
    snake-case.
    """
    def __init__(self):
        super().__init__('template_folder_name', default=_missing, inherit=False)

    def get_value(self, meta, base_classes_meta, mcs_args: McsArgs):
        value = super().get_value(meta, base_classes_meta, mcs_args)
        if value is not _missing:
            return value

        return controller_name(mcs_args.name, mcs_args.getattr(REMOVE_SUFFIXES_ATTR))

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        assert isinstance(value, str) and os.sep not in value, \
            f'The {self.name} meta option must be a string and not a full path'


class _ControllerTemplateFileExtensionMetaOption(MetaOption):
    """
    The filename extension to use for templates for this controller's views.
    Defaults to your app config's ``TEMPLATE_FILE_EXTENSION`` setting, and
    overrides it if set.
    """
    def __init__(self):
        super().__init__('template_file_extension', default=None, inherit=False)

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        assert isinstance(value, str), \
            f'The {self.name} meta option must be a string'


class _ControllerUrlPrefixMetaOption(MetaOption):
    """
    The url prefix to use for all routes from this controller. Defaults to the class name,
    with the suffixes ``Controller`` or ``View`` stripped, stopping after the first found
    (if any). The resulting value is ``f'/{snake_case(pluralize(value))}'``.
    """
    def __init__(self):
        super().__init__('url_prefix', default=None, inherit=False)

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        assert isinstance(value, str), \
            f'The {self.name} meta option must be a string'


class _ControllerMetaOptionsFactory(MetaOptionsFactory):
    _options = [
        _ControllerAbstractMetaOption,
        _ControllerDecoratorsMetaOption,
        _ControllerTemplateFolderNameMetaOption,
        _ControllerTemplateFileExtensionMetaOption,
        _ControllerUrlPrefixMetaOption,
    ]


class Controller(metaclass=_ControllerMetaclass):
    """
    Base class for class-based views in Flask Unchained.
    """
    _meta_options_factory_class = _ControllerMetaOptionsFactory
    _view_funcs = {}

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
        :param ctx: Context variables to pass into the template.
        """
        if '.' not in template_name:
            template_file_extension = (self.Meta.template_file_extension
                                       or app.config.TEMPLATE_FILE_EXTENSION)
            template_name = f'{template_name}{template_file_extension}'
        if self.Meta.template_folder_name and os.sep not in template_name:
            template_name = os.path.join(self.Meta.template_folder_name,
                                         template_name)
        return render_template(template_name, **ctx)

    def redirect(self,
                 where: Optional[str] = None,
                 default: Optional[str] = None,
                 override: Optional[str] = None,
                 **url_kwargs):
        """
        Convenience method for returning redirect responses.

        :param where: A URL, endpoint, or config key name to redirect to.
        :param default: A URL, endpoint, or config key name to redirect to if
                        ``where`` is invalid.
        :param override: explicitly redirect to a URL, endpoint, or config key name
                         (takes precedence over the ``next`` value in query strings
                         or forms)
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
        """
        this code, combined with apply_decorators and dispatch_request, is
        95% taken from Flask's View.as_view classmethod (albeit refactored)
        differences:

        - we pass method_name to dispatch_request, to allow for easier
          customization of behavior by subclasses
        - we apply decorators later, so they get called when the view does

        FIXME: maybe this last bullet point is a horrible idea???
        - we also apply them in reverse, so that they get applied in the
          logical top-to-bottom order as declared in controllers
        """
        if method_name not in cls._view_funcs:
            def view_func(*args, **kwargs):
                self = view_func.view_class(*class_args, **class_kwargs)
                return self.dispatch_request(method_name, *args, **kwargs)

            wrapper_assignments = (set(functools.WRAPPER_ASSIGNMENTS)
                                   .difference({'__qualname__'}))
            functools.update_wrapper(view_func, getattr(cls, method_name),
                                     assigned=list(wrapper_assignments))
            view_func.view_class = cls
            cls._view_funcs[method_name] = view_func

        return cls._view_funcs[method_name]

    def dispatch_request(self, method_name, *view_args, **view_kwargs):
        decorators = self.get_decorators(method_name)
        method = self.apply_decorators(getattr(self, method_name), decorators)
        return method(*view_args, **view_kwargs)

    def get_decorators(self, method_name):
        return self.Meta.decorators or []

    def apply_decorators(self, view_func, decorators):
        if not decorators:
            return view_func

        original_view_func = view_func
        for decorator in reversed(decorators):
            view_func = decorator(view_func)
        functools.update_wrapper(view_func, original_view_func)
        return view_func


__all__ = [
    'Controller',
]
