import importlib

from flask import Blueprint
from flask_unchained import FlaskUnchained
from py_meta_utils import _missing
from typing import *

from .attr_constants import CONTROLLER_ROUTES_ATTR, FN_ROUTES_ATTR
from .controller import Controller
from .resource import Resource
from .route import Route
from .utils import join, method_name_to_url, rename_parent_resource_param_name

Defaults = Dict[str, Any]
Endpoints = Union[List[str], Tuple[str], Set[str]]
Methods = Union[List[str], Tuple[str], Set[str]]
RouteGenerator = Iterable[Route]


def controller(url_prefix_or_controller_cls: Union[str, Type[Controller]],
               controller_cls: Optional[Type[Controller]] = None,
               *,
               rules: Optional[Iterable[Union[Route, RouteGenerator]]] = None,
               ) -> RouteGenerator:
    """
    This function is used to register a controller class's routes.

    Example usage::

        routes = lambda: [
            controller(SiteController),
        ]

    Or with the optional prefix argument::

        routes = lambda: [
            controller('/products', ProductController),
        ]

    Specify ``rules`` to only include those routes from the controller::

        routes = lambda: [
            controller(SecurityController, rules=[
               rule('/login', SecurityController.login),
               rule('/logout', SecurityController.logout),
               rule('/sign-up', SecurityController.register),
            ]),
        ]

    :param url_prefix_or_controller_cls: The controller class, or a url prefix for
                                         all of the rules from the controller class
                                         passed as the second argument
    :param controller_cls: If a url prefix was given as the first argument, then
                           the controller class must be passed as the second argument
    :param rules: An optional list of rules to limit/customize the routes included
                  from the controller
    """
    url_prefix, controller_cls = _normalize_args(
        url_prefix_or_controller_cls, controller_cls, _is_controller_cls)
    url_prefix = url_prefix or controller_cls.Meta.url_prefix

    routes = []
    controller_routes = getattr(controller_cls, CONTROLLER_ROUTES_ATTR)
    if rules is None:
        routes = controller_routes.values()
    else:
        for route in _reduce_routes(rules):
            existing = controller_routes.get(route.method_name)
            if existing:
                routes.append(_inherit_route_options(route, existing[0]))
            else:
                routes.append(route)

    yield from _normalize_controller_routes(routes, controller_cls,
                                            url_prefix=url_prefix)


def delete(rule: str,
           cls_method_name_or_view_fn: Optional[Union[str, Callable]] = None,
           *,
           defaults: Optional[Defaults] = _missing,
           endpoint: Optional[str] = _missing,
           is_member: Optional[bool] = _missing,
           only_if: Optional[Union[bool, Callable[[FlaskUnchained], bool]]] = _missing,
           **rule_options) -> RouteGenerator:
    """
    Like :func:`rule`, except specifically for HTTP DELETE requests.

    :param rule: The url rule for this route.
    :param cls_method_name_or_view_fn: The view function for this route.
    :param is_member: Whether or not this route is a member function.
    :param only_if: An optional function to decide at runtime whether or not to register
                    the route with Flask. It gets passed the configured app as a single
                    argument, and should return a boolean.
    :param rule_options: Keyword arguments that ultimately end up getting passed on to
                         :class:`~werkzeug.routing.Rule`
    """
    rule_options.pop('methods', None)
    yield Route(rule, cls_method_name_or_view_fn, defaults=defaults,
                endpoint=endpoint, is_member=is_member, methods=['DELETE'],
                only_if=only_if, **rule_options)


def func(rule_or_view_func: Union[str, Callable],
         view_func: Optional[Callable] = _missing,
         blueprint: Optional[Blueprint] = _missing,
         defaults: Optional[Defaults] = _missing,
         endpoint: Optional[str] = _missing,
         methods: Optional[Methods] = _missing,
         only_if: Optional[Union[bool, Callable[[FlaskUnchained], bool]]] = _missing,
         **rule_options,
         ) -> RouteGenerator:
    """
    This function allows to register legacy view functions as routes, eg::

        @route('/')
        def index():
            return render_template('site/index.html')

        routes = lambda: [
            func(index),
        ]

    It accepts an optional url rule argument::

        routes = lambda: [
            func('/products', product_list_view),
        ]

    As well as supporting the same kwargs as Werkzeug's :class:`~werkzeug.routing.Rule`,
    eg::

        routes = lambda: [
            func('/', index, endpoint='home', methods=['GET', 'POST']),
        ]

    :param rule_or_view_func: The view function, or an optional url rule for the view
                              function given as the second argument
    :param view_func: The view function if passed a url rule as the first argument
    :param only_if: An optional function to decide at runtime whether or not to register
                    the route with Flask. It gets passed the configured app as a single
                    argument, and should return a boolean.
    :param rule_options: Keyword arguments that ultimately end up getting passed on to
                         :class:`~werkzeug.routing.Rule`
    """
    rule, view_func = _normalize_args(
        rule_or_view_func, view_func, _is_view_func)

    route = Route(rule, view_func, blueprint=blueprint, defaults=defaults,
                  endpoint=endpoint, methods=methods, only_if=only_if,
                  **rule_options)

    existing_routes = getattr(view_func, FN_ROUTES_ATTR, [])
    if len(existing_routes) == 1:
        existing_route = existing_routes[0]
    else:
        routes_by_rule = {route.rule: route for route in existing_routes}
        lookup_rule = (rule if isinstance(rule, str)
                       else method_name_to_url(view_func.__name__))
        existing_route = routes_by_rule.get(lookup_rule, None)

    if not existing_route:
        yield route
    else:
        yield _inherit_route_options(route, existing_route)


def get(rule: str,
        cls_method_name_or_view_fn: Optional[Union[str, Callable]] = None,
        *,
        defaults: Optional[Defaults] = _missing,
        endpoint: Optional[str] = _missing,
        is_member: Optional[bool] = _missing,
        only_if: Optional[Union[bool, Callable[[FlaskUnchained], bool]]] = _missing,
        **rule_options,
        ) -> RouteGenerator:
    """
    Like :func:`rule`, except specifically for HTTP GET requests.

    :param rule: The url rule for this route.
    :param cls_method_name_or_view_fn: The view function for this route.
    :param is_member: Whether or not this route is a member function.
    :param only_if: An optional function to decide at runtime whether or not to register
                    the route with Flask. It gets passed the configured app as a single
                    argument, and should return a boolean.
    :param rule_options: Keyword arguments that ultimately end up getting passed on to
                         :class:`~werkzeug.routing.Rule`
    """
    rule_options.pop('methods', None)
    yield Route(rule, cls_method_name_or_view_fn, defaults=defaults,
                endpoint=endpoint, is_member=is_member, methods=['GET'],
                only_if=only_if, **rule_options)


def include(url_prefix_or_module_name: str,
            module_name: Optional[str] = None,
            *,
            attr: str = 'routes',
            exclude: Optional[Endpoints] = None,
            only: Optional[Endpoints] = None,
            ) -> RouteGenerator:
    """
    Include the routes from another module at that point in the tree. For example::

        # project-root/bundles/primes/routes.py
        routes = lambda: [
            controller('/two', TwoController),
            controller('/three', ThreeController),
            controller('/five', FiveController),
        ]


        # project-root/bundles/blog/routes.py
        routes = lambda: [
            func('/', index),
            controller('/authors', AuthorController),
            controller('/posts', PostController),
        ]


        # project-root/your_app_bundle/routes.py
        routes = lambda: [
            include('some_bundle.routes'),

            # these last two are equivalent
            include('/blog', 'bundles.blog.routes'),
            prefix('/blog', [
                include('bundles.blog.routes'),
            ]),
        ]

    :param url_prefix_or_module_name: The module name, or a url prefix for all
                                      of the included routes in the module name
                                      passed as the second argument.
    :param module_name: The module name of the routes to include if a url prefix
                        was given as the first argument.
    :param attr: The attribute name in the module, if different from ``routes``.
    :param exclude: An optional list of endpoints to exclude.
    :param only: An optional list of endpoints to only include.
    """
    url_prefix = None
    if module_name is None:
        module_name = url_prefix_or_module_name
    else:
        url_prefix = url_prefix_or_module_name

    module = importlib.import_module(module_name)
    try:
        routes = getattr(module, attr)()
    except AttributeError:
        raise AttributeError(f'Could not find a variable named `{attr}` '
                             f'in the {module_name} module!')

    routes = _reduce_routes(routes, exclude=exclude, only=only)
    if url_prefix:
        yield from prefix(url_prefix, routes)
    else:
        yield from routes


def patch(rule: str,
          cls_method_name_or_view_fn: Optional[Union[str, Callable]] = None,
          *,
          defaults: Optional[Defaults] = _missing,
          endpoint: Optional[str] = _missing,
          is_member: Optional[bool] = _missing,
          only_if: Optional[Union[bool, Callable[[FlaskUnchained], bool]]] = _missing,
          **rule_options,
          ) -> RouteGenerator:
    """
    Like :func:`rule`, except specifically for HTTP PATCH requests.

    :param rule: The url rule for this route.
    :param cls_method_name_or_view_fn: The view function for this route.
    :param is_member: Whether or not this route is a member function.
    :param only_if: An optional function to decide at runtime whether or not to register
                    the route with Flask. It gets passed the configured app as a single
                    argument, and should return a boolean.
    :param rule_options: Keyword arguments that ultimately end up getting passed on to
                         :class:`~werkzeug.routing.Rule`
    """
    rule_options.pop('methods', None)
    yield Route(rule, cls_method_name_or_view_fn, defaults=defaults,
                endpoint=endpoint, is_member=is_member, methods=['PATCH'],
                only_if=only_if, **rule_options)


def post(rule: str,
         cls_method_name_or_view_fn: Optional[Union[str, Callable]] = None,
         *,
         defaults: Optional[Defaults] = _missing,
         endpoint: Optional[str] = _missing,
         is_member: Optional[bool] = _missing,
         only_if: Optional[Union[bool, Callable[[FlaskUnchained], bool]]] = _missing,
         **rule_options,
         ) -> RouteGenerator:
    """
    Like :func:`rule`, except specifically for HTTP POST requests.

    :param rule: The url rule for this route.
    :param cls_method_name_or_view_fn: The view function for this route.
    :param is_member: Whether or not this route is a member function.
    :param only_if: An optional function to decide at runtime whether or not to register
                    the route with Flask. It gets passed the configured app as a single
                    argument, and should return a boolean.
    :param rule_options: Keyword arguments that ultimately end up getting passed on to
                         :class:`~werkzeug.routing.Rule`
    """
    rule_options.pop('methods', None)
    yield Route(rule, cls_method_name_or_view_fn, defaults=defaults,
                endpoint=endpoint, is_member=is_member, methods=['POST'],
                only_if=only_if, **rule_options)


def prefix(url_prefix: str,
           children: Iterable[Union[Route, RouteGenerator]],
           ) -> RouteGenerator:
    """
    Sets a prefix on all of the child routes passed to it. It also supports nesting, eg::

        routes = lambda: [
            prefix('/foobar', [
                controller('/one', OneController),
                controller('/two', TwoController),
                prefix('/baz', [
                    controller('/three', ThreeController),
                    controller('/four', FourController),
                ])
            ])
        ]

    :param url_prefix: The url prefix to set on the child routes
    :param children:
    """
    for route in _reduce_routes(children):
        route = route.copy()
        route.rule = join(url_prefix, route.rule,
                          trailing_slash=route.rule.endswith('/'))
        yield route


def put(rule: str,
        cls_method_name_or_view_fn: Optional[Union[str, Callable]] = None,
        *,
        defaults: Optional[Defaults] = _missing,
        endpoint: Optional[str] = _missing,
        is_member: Optional[bool] = _missing,
        only_if: Optional[Union[bool, Callable[[FlaskUnchained], bool]]] = _missing,
        **rule_options,
        ) -> RouteGenerator:
    """
    Like :func:`rule`, except specifically for HTTP PUT requests.

    :param rule: The url rule for this route.
    :param cls_method_name_or_view_fn: The view function for this route.
    :param is_member: Whether or not this route is a member function.
    :param only_if: An optional function to decide at runtime whether or not to register
                    the route with Flask. It gets passed the configured app as a single
                    argument, and should return a boolean.
    :param rule_options: Keyword arguments that ultimately end up getting passed on to
                         :class:`~werkzeug.routing.Rule`
    """
    rule_options.pop('methods', None)
    yield Route(rule, cls_method_name_or_view_fn, defaults=defaults,
                endpoint=endpoint, is_member=is_member, methods=['PUT'],
                only_if=only_if, **rule_options)


def resource(url_prefix_or_resource_cls: Union[str, Type[Resource]],
             resource_cls: Optional[Type[Resource]] = None,
             *,
             member_param: Optional[str] = None,
             unique_member_param: Optional[str] = None,
             rules: Optional[Iterable[Union[Route, RouteGenerator]]] = None,
             subresources: Optional[Iterable[RouteGenerator]] = None,
             ) -> RouteGenerator:
    """
    This function is used to register a :class:`Resource`'s routes.

    Example usage::

        routes = lambda: [
            prefix('/api/v1', [
                resource('/products', ProductResource),
            ])
        ]

    Or with the optional prefix argument::

        routes = lambda: [
            resource('/products', ProductResource),
        ]

    Specify ``rules`` to only include those routes from the resource::

        routes = lambda: [
            resource('/users', UserResource, rules=[
               get('/', UserResource.list),
               get('/<int:id>', UserResource.get),
            ]),
        ]

    Specify ``subresources`` to nest resource routes::

        routes = lambda: [
            resource('/users', UserResource, subresources=[
               resource('/roles', RoleResource)
            ]),
        ]

    Subresources can be nested as deeply as you want, however it's not recommended
    to go more than two or three levels deep at the most, otherwise your URLs will
    become unwieldy.

    :param url_prefix_or_resource_cls: The resource class, or a url prefix for
                                       all of the rules from the resource class
                                       passed as the second argument.
    :param resource_cls: If a url prefix was given as the first argument, then
                         the resource class must be passed as the second argument.
    :param member_param: Optionally override the controller's member_param attribute.
    :param rules: An optional list of rules to limit/customize the routes included
                  from the resource.
    :param subresources: An optional list of subresources.
    """
    url_prefix, resource_cls = _normalize_args(
        url_prefix_or_resource_cls, resource_cls, _is_resource_cls)
    member_param = member_param or resource_cls.Meta.member_param
    unique_member_param = unique_member_param or resource_cls.Meta.unique_member_param
    url_prefix = url_prefix or resource_cls.Meta.url_prefix

    routes = getattr(resource_cls, CONTROLLER_ROUTES_ATTR)
    if rules is not None:
        routes = {method_name: method_routes
                  for method_name, method_routes in routes.items()
                  if method_name in resource_cls.resource_methods}
        for route in rules:
            routes[route.method_name] = route

    yield from _normalize_controller_routes(routes.values(), resource_cls,
                                            url_prefix=url_prefix,
                                            member_param=member_param,
                                            unique_member_param=unique_member_param)

    for subroute in _reduce_routes(subresources):
        subroute._parent_resource_cls = resource_cls
        subroute._parent_member_param = member_param
        subroute._unique_member_param = unique_member_param
        subroute = subroute.copy()
        subroute.rule = rename_parent_resource_param_name(
            subroute, rule=join(url_prefix, member_param, subroute.rule,
                                trailing_slash=subroute.rule.endswith('/')))
        yield subroute


def rule(rule: str,
         cls_method_name_or_view_fn: Optional[Union[str, Callable]] = None,
         *,
         defaults: Optional[Defaults] = _missing,
         endpoint: Optional[str] = _missing,
         is_member: Optional[bool] = _missing,
         methods: Optional[Methods] = _missing,
         only_if: Optional[Union[bool, Callable[[FlaskUnchained], bool]]] = _missing,
         **rule_options,
         ) -> RouteGenerator:
    """
    Used to specify customizations to the route settings of class-based view function.
    For example::

        routes = lambda: [
            prefix('/api/v1', [
                controller(SecurityController, rules=[
                   rule('/login', SecurityController.login,
                        endpoint='security_api.login'),
                   rule('/logout', SecurityController.logout,
                        endpoint='security_api.logout'),
                   rule('/sign-up', SecurityController.register,
                        endpoint='security_api.register'),
                ]),
            ],
        ]

    :param rule: The URL rule.
    :param cls_method_name_or_view_fn: The view function.
    :param defaults: Any default values for parameters in the URL rule.
    :param endpoint: The endpoint name of this view. Determined automatically if left
                     unspecified.
    :param is_member: Whether or not this view is for a
                      :class:`~flask_unchained.bundles.resource.resource.Resource`
                      member method.
    :param methods: A list of HTTP methods supported by this view. Defaults to
                    ``['GET']``.
    :param only_if: A boolean or callable to dynamically determine whether or not to
                    register this route with the app.
    :param rule_options: Other kwargs passed on to :class:`~werkzeug.routing.Rule`.
    """
    yield Route(rule, cls_method_name_or_view_fn, defaults=defaults,
                endpoint=endpoint, is_member=is_member, methods=methods,
                only_if=only_if, **rule_options)


def _inherit_route_options(parent: Route, child: Route):
    if parent._blueprint is _missing:
        parent.blueprint = child.blueprint
    if parent._defaults is _missing:
        parent.defaults = child.defaults
    if parent._endpoint is _missing:
        parent.endpoint = child.endpoint
    if parent._is_member is _missing:
        parent.is_member = child.is_member
    if parent._methods is _missing:
        parent.methods = child.methods
    if parent._only_if is _missing:
        parent.only_if = child.only_if
    parent.rule_options = {**child.rule_options, **parent.rule_options}
    return parent


def _is_controller_cls(controller_cls, has_rule):
    is_controller = (isinstance(controller_cls, type)
                     and issubclass(controller_cls, Controller))
    is_resource = is_controller and issubclass(controller_cls, Resource)
    if is_controller and not is_resource:
        return True
    elif is_resource:
        raise TypeError(f'please use the resource function to include '
                        f'{controller_cls}')

    if has_rule:
        raise ValueError('the `controller_cls` argument is required when the '
                         'first argument to controller is a url prefix')
    else:
        raise ValueError('call to controller missing rule and/or '
                         'controller_cls arguments')


def _is_resource_cls(resource_cls, has_rule):
    if isinstance(resource_cls, type) and issubclass(resource_cls, Resource):
        return True

    if has_rule:
        raise ValueError('the `resource_cls` argument is required when the '
                         'first argument to resource is a url prefix')
    else:
        raise ValueError('call to resource missing rule and/or '
                         'resource_cls arguments')


def _is_view_func(view_func, has_rule):
    if callable(view_func):
        return True

    if has_rule:
        raise ValueError('the `view_func` argument is required when the '
                         'first argument to func is a url rule')
    else:
        raise ValueError('the `view_func` argument must be callable')


def _normalize_args(maybe_str, maybe_none, test):
    try:
        if isinstance(maybe_str, str):
            rule = maybe_str
            if test(maybe_none, has_rule=True):
                return rule, maybe_none
        elif test(maybe_str, has_rule=False):
            return None, maybe_str
    except ValueError as e:
        raise ValueError(f'{str(e)} (got {maybe_str}, {maybe_none})')


def _normalize_controller_routes(rules: Iterable[Route],
                                 controller_cls: Type[Controller],
                                 url_prefix: Optional[str] = None,
                                 member_param: Optional[str] = None,
                                 unique_member_param: Optional[str] = None,
                                 ) -> RouteGenerator:
    for route in _reduce_routes(rules):
        route = route.copy()
        route._member_param = member_param
        route._unique_member_param = unique_member_param
        route.rule = route._make_rule(url_prefix, member_param=member_param)
        route.view_func = controller_cls.method_as_view(route.method_name)
        yield route


def _reduce_routes(routes: Iterable[Union[Route, RouteGenerator]],
                   exclude: Optional[Endpoints] = None,
                   only: Optional[Endpoints] = None,
                   ) -> RouteGenerator:
    if not routes:
        return ()

    for route in routes:
        if isinstance(route, Route):
            excluded = exclude and route.endpoint in exclude
            not_included = only and route.endpoint not in only
            if not (excluded or not_included):
                yield route
        else:
            yield from _reduce_routes(route, exclude=exclude, only=only)


__all__ = [
    # types
    'Defaults',
    'Endpoints',
    'Methods',
    'RouteGenerator',

    # public api
    'controller',
    'resource',
    'func',
    'include',
    'prefix',
    'get',
    'delete',
    'post',
    'patch',
    'put',
    'rule'
]
