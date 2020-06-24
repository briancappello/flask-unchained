from collections import defaultdict
from flask_unchained import Bundle, FlaskUnchained
from flask_unchained.constants import DEV, TEST
from typing import *

from .constants import (
    ALL_RESOURCE_METHODS, RESOURCE_INDEX_METHODS, RESOURCE_MEMBER_METHODS,
    CREATE, DELETE, GET, LIST, PATCH, PUT)
from .controller import Controller
from .decorators import param_converter, no_route, route
from .resource import Resource
from .route import Route
from .routes import (
    controller, delete, func, get, include, patch, post, prefix, put, resource, rule)
from .utils import StringConverter, redirect, url_for


class ControllerBundle(Bundle):
    """
    The Controller Bundle.
    """

    name = 'controller_bundle'
    """
    The name of the Controller Bundle.
    """

    _has_views = False

    def __init__(self):
        # these all get populated by the RegisterRoutesHook

        self.endpoints: Dict[str, List[Route]] = defaultdict(list)
        """
        Lookup of routes by endpoint name.
        """

        self.controller_endpoints: Dict[str, List[Route]] = defaultdict(list)
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
                             'cache_size': 0 if app.env in {DEV, TEST} else 400,
                             'loader': UnchainedJinjaLoader(app)}
        app.jinja_env.globals['url_for'] = url_for

        for name in ['string', 'str']:
            app.url_map.converters[name] = StringConverter


__all__ = [
    'ControllerBundle',
    'Controller',
    'Resource',
    'route',
    'no_route',
    'param_converter',
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
