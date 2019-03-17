from collections import defaultdict
from flask_unchained import Bundle, FlaskUnchained
from typing import *

from .constants import (ALL_METHODS, INDEX_METHODS, MEMBER_METHODS,
                        CREATE, DELETE, GET, LIST, PATCH, PUT)
from .controller import Controller
from .decorators import no_route, route
from .resource import Resource
from .route import Route
from .routes import (
    controller, delete, func, get, include, patch, post, prefix, put, resource, rule)
from .utils import StringConverter, redirect, url_for


class ControllerBundle(Bundle):
    """
    The :class:`~flask_unchained.Bundle` subclass for the controller bundle.
    """

    def __init__(self):

        self.endpoints: Dict[str, Route] = defaultdict(list)
        """
        Lookup of routes by endpoint name.
        """

        self.controller_endpoints: Dict[str, Route] = defaultdict(list)
        """
        Lookup of routes by keys: f'{ControllerClassName}.{view_method_name}'
        """

        self.bundle_routes: Dict[str, List[Route]] = defaultdict(list)
        """
        Lookup of routes belonging to each bundle by bundle name.
        """

        self.other_routes: List[Route] = []
        """
        List of routes not associated with any bundles.
        """

    def before_init_app(self, app: FlaskUnchained):
        """
        Configure the Jinja environment and template loader.
        """
        from .templates import (UnchainedJinjaEnvironment,
                                UnchainedJinjaLoader)
        app.jinja_environment = UnchainedJinjaEnvironment
        app.jinja_options = {**app.jinja_options,
                             'loader': UnchainedJinjaLoader(app)}
        app.jinja_env.globals['url_for'] = url_for

        for name in ['string', 'str']:
            app.url_map.converters[name] = StringConverter

    def after_init_app(self, app: FlaskUnchained):
        """
        Configure an after request hook to set the ``csrf_token`` in the cookie.
        """

        from flask_wtf.csrf import generate_csrf

        # send CSRF token in the cookie
        @app.after_request
        def set_csrf_cookie(response):
            if response:
                response.set_cookie('csrf_token', generate_csrf())
            return response


__all__ = [
    'ControllerBundle',
    'Controller',
    'Resource',
    'route',
    'no_route',
    'controller',
    'func',
    'get',
    'include',
    'patch',
    'post',
    'prefix',
    'put',
    'resource',
    'rule',
    'redirect',
    'url_for',
]
