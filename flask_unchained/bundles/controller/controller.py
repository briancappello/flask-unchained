import functools
import os

from flask import (after_this_request, current_app as app, flash, jsonify,
                   render_template, request)
from http import HTTPStatus

from .metaclasses import ControllerMeta
from .utils import controller_name, redirect


class TemplateFolderDescriptor:
    def __get__(self, instance, cls):
        return controller_name(cls)


class Controller(metaclass=ControllerMeta):
    """
    Base class for controller views.
    """
    __abstract__ = True

    template_folder = TemplateFolderDescriptor()
    """
    Path to the template folder for this bundle. By default, it will use a ``templates``
    folder in the bundle package, if it exists, otherwise None.
    """

    template_extension = '.html'
    """
    The default filename extension to use for templates.
    """

    # FIXME: is this still supported? probably shouldn't be
    blueprint = None

    decorators = None
    """
    A list of decorators to apply to *all* views in this controller.
    """

    url_prefix = None
    """
    A URL prefix to apply to all views in this controller.
    """

    def flash(self, msg, category=None):
        """
        Convenience method for flashing messages.

        :param msg: The message to flash.
        :param category: The category of the message.
        """
        if not request.is_json and app.config.get('FLASH_MESSAGES', True):
            flash(msg, category)

    def render(self, template_name, **ctx):
        """
        Convenience method for rendering a template.

        :param template_name: The template's name. Can either be a full path,
                              or a filename in the controller's template folder.
        :param ctx: Context variables to pass into the template.
        """
        if '.' not in template_name:
            template_name = f'{template_name}{self.template_extension}'
        if self.template_folder and os.sep not in template_name:
            template_name = os.path.join(self.template_folder, template_name)
        return render_template(template_name, **ctx)

    def redirect(self, where=None, default=None, override=None, **url_kwargs):
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

    def jsonify(self, data, code=HTTPStatus.OK, headers=None):
        """
        Convenience method to return json responses.

        :param data: The python data to jsonify.
        :param code: The HTTP status code to return.
        :param headers: Any optional headers.
        """
        return jsonify(data), code, headers or {}

    def errors(self, errors, code=HTTPStatus.BAD_REQUEST, key='errors', headers=None):
        """
        Convenience method to return errors as json.

        :param errors: The list of errors.
        :param code: The HTTP status code.
        :param key: The key to return the errors under.
        :param headers: Any optional headers.
        """
        return jsonify({key: errors}), code, headers or {}

    def after_this_request(self, fn):
        after_this_request(fn)

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
        def view_func(*args, **kwargs):
            self = view_func.view_class(*class_args, **class_kwargs)
            return self.dispatch_request(method_name, *args, **kwargs)

        wrapper_assignments = (set(functools.WRAPPER_ASSIGNMENTS)
                               .difference({'__qualname__'}))
        functools.update_wrapper(view_func, getattr(cls, method_name),
                                 assigned=list(wrapper_assignments))
        view_func.view_class = cls
        return view_func

    def dispatch_request(self, method_name, *view_args, **view_kwargs):
        decorators = self.get_decorators(method_name)
        method = self.apply_decorators(getattr(self, method_name), decorators)
        return method(*view_args, **view_kwargs)

    def get_decorators(self, method_name):
        return self.decorators or []

    def apply_decorators(self, view_func, decorators):
        if not decorators:
            return view_func

        original_view_func = view_func
        for decorator in reversed(decorators):
            view_func = decorator(view_func)
        functools.update_wrapper(view_func, original_view_func)
        return view_func
