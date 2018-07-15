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
    __abstract__ = True

    template_folder = TemplateFolderDescriptor()
    template_extension = '.html'

    blueprint = None
    decorators = None
    url_prefix = None

    def flash(self, msg, category=None):
        if not request.is_json and app.config.get('FLASH_MESSAGES', True):
            flash(msg, category)

    def redirect(self, where=None, default=None, override=None, **url_kwargs):
        return redirect(where, default, override, _cls=self, **url_kwargs)

    def render(self, template_name, **ctx):
        if '.' not in template_name:
            template_name = f'{template_name}{self.template_extension}'
        if self.template_folder and os.sep not in template_name:
            template_name = os.path.join(self.template_folder, template_name)
        return render_template(template_name, **ctx)

    @classmethod
    def method_as_view(cls, method_name, *class_args, **class_kwargs):
        # this code, combined with apply_decorators and dispatch_request, is
        # 95% taken from Flask's View.as_view classmethod (albeit refactored)
        # differences:
        # - we pass method_name to dispatch_request, to allow for easier
        #   customization of behavior by subclasses
        # - we apply decorators later, so they get called when the view does
        # - we also apply them in reverse, so that they get applied in the
        #   logical top-to-bottom order as declared in controllers
        def view_func(*args, **kwargs):
            self = view_func.view_class(*class_args, **class_kwargs)
            return self.dispatch_request(method_name, *args, **kwargs)

        wrapper_assignments = (set(functools.WRAPPER_ASSIGNMENTS)
                               .difference({'__qualname__'}))
        functools.update_wrapper(view_func, getattr(cls, method_name),
                                 assigned=wrapper_assignments)
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

    def after_this_request(self, fn):
        after_this_request(fn)

    def jsonify(self, data, code=HTTPStatus.OK, headers=None):
        return jsonify(data), code, headers or {}

    def errors(self, errors, code=HTTPStatus.BAD_REQUEST, key='errors', headers=None):
        return jsonify({key: errors}), code, headers or {}
