import importlib
import inspect
import sys

from flask import Blueprint, Flask
from typing import *

from .attr_constants import CONTROLLER_ROUTES_ATTR, FN_ROUTES_ATTR
from .constants import _missing
from .controller import Controller
from .resource import Resource
from .route import Route
from .utils import join, method_name_to_url

Defaults = Dict[str, Any]
Endpoints = Union[List[str], Tuple[str], Set[str]]
Methods = Union[List[str], Tuple[str], Set[str]]
RouteGenerator = Iterable[Route]


def controller(url_prefix_or_controller_cls: Union[str, Type[Controller]],
               controller_cls: Optional[Type[Controller]] = None,
               *,
               rules: Optional[Iterable[Union[Route, RouteGenerator]]] = None,
               ) -> RouteGenerator:
    url_prefix, controller_cls = _normalize_args(
        url_prefix_or_controller_cls, controller_cls, _is_controller_cls)

    # FIXME this business of needing to set and then restore the class's
    # url_prefix is kinda very crap. (also applies in the resource function)
    controller_url_prefix = controller_cls.url_prefix
    if url_prefix:
        controller_cls.url_prefix = url_prefix

    routes = []
    controller_routes = getattr(controller_cls, CONTROLLER_ROUTES_ATTR)
    if rules is None:
        routes = controller_routes.values()
    else:
        for route in reduce_routes(rules):
            existing = controller_routes.get(route.method_name)
            if existing:
                routes.append(_inherit_route_options(route, existing[0]))
            else:
                routes.append(route)

    yield from _normalize_controller_routes(routes, controller_cls)

    controller_cls.url_prefix = controller_url_prefix


def func(rule_or_view_func: Union[str, Callable],
         view_func: Optional[Callable] = _missing,
         blueprint: Optional[Blueprint] = _missing,
         defaults: Optional[Defaults] = _missing,
         endpoint: Optional[str] = _missing,
         methods: Optional[Methods] = _missing,
         only_if: Optional[Union[bool, Callable[[Flask], bool]]] = _missing,
         **rule_options,
         ) -> RouteGenerator:
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
        only_if: Optional[Union[bool, Callable[[Flask], bool]]] = _missing,
        **rule_options,
        ) -> RouteGenerator:
    rule_options.pop('methods', None)
    yield Route(rule, cls_method_name_or_view_fn, defaults=defaults,
                endpoint=endpoint, is_member=is_member, methods=['GET'],
                only_if=only_if, **rule_options)


def include(module_name: str,
            *,
            attr: str = 'routes',
            exclude: Optional[Endpoints] = None,
            only: Optional[Endpoints] = None,
            ) -> RouteGenerator:
    # because routes are generators, once they've been "drained", they can't be
    # used again. under normal end-user-app circumstances this reload probably
    # wouldn't be needed, but it's at least required for the tests to pass
    if module_name in sys.modules:
        del sys.modules[module_name]
    module = importlib.import_module(module_name)

    try:
        routes = reduce_routes(getattr(module, attr))
    except AttributeError:
        raise AttributeError(f'Could not find a variable named `{attr}` '
                             f'in the {module_name} module!')

    def should_include_route(route):
        excluded = exclude and route.endpoint in exclude
        not_included = only and route.endpoint not in only
        if excluded or not_included:
            return False
        return True

    for route in routes:
        if should_include_route(route):
            yield route


def patch(rule: str,
          cls_method_name_or_view_fn: Optional[Union[str, Callable]] = None,
          *,
          defaults: Optional[Defaults] = _missing,
          endpoint: Optional[str] = _missing,
          is_member: Optional[bool] = _missing,
          only_if: Optional[Union[bool, Callable[[Flask], bool]]] = _missing,
          **rule_options,
          ) -> RouteGenerator:
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
         only_if: Optional[Union[bool, Callable[[Flask], bool]]] = _missing,
         **rule_options,
         ) -> RouteGenerator:
    rule_options.pop('methods', None)
    yield Route(rule, cls_method_name_or_view_fn, defaults=defaults,
                endpoint=endpoint, is_member=is_member, methods=['POST'],
                only_if=only_if, **rule_options)


def prefix(url_prefix: str,
           children: Iterable[Union[Route, RouteGenerator]],
           ) -> RouteGenerator:
    for route in reduce_routes(children):
        route = route.copy()
        route.rule = join(url_prefix, route.rule)
        yield route


def put(rule: str,
        cls_method_name_or_view_fn: Optional[Union[str, Callable]] = None,
        *,
        defaults: Optional[Defaults] = _missing,
        endpoint: Optional[str] = _missing,
        is_member: Optional[bool] = _missing,
        only_if: Optional[Union[bool, Callable[[Flask], bool]]] = _missing,
        **rule_options,
        ) -> RouteGenerator:
    rule_options.pop('methods', None)
    yield Route(rule, cls_method_name_or_view_fn, defaults=defaults,
                endpoint=endpoint, is_member=is_member, methods=['PUT'],
                only_if=only_if, **rule_options)


def resource(url_prefix_or_resource_cls: Union[str, Type[Resource]],
             resource_cls: Optional[Type[Resource]] = None,
             *,
             rules: Optional[Iterable[Union[Route, RouteGenerator]]] = None,
             subresources: Optional[Iterable[RouteGenerator]] = None,
             ) -> RouteGenerator:
    url_prefix, resource_cls = _normalize_args(
        url_prefix_or_resource_cls, resource_cls, _is_resource_cls)

    resource_url_prefix = resource_cls.url_prefix
    if url_prefix:
        resource_cls.url_prefix = url_prefix

    routes = getattr(resource_cls, CONTROLLER_ROUTES_ATTR)
    if rules is not None:
        routes = {method_name: method_routes
                  for method_name, method_routes in routes.items()
                  if method_name in resource_cls.resource_methods}
        for route in rules:
            routes[route.method_name] = route

    yield from _normalize_controller_routes(routes.values(), resource_cls)

    for subroute in reduce_routes(subresources):
        subroute = subroute.copy()

        # can't have a subresource with a different blueprint than its parent
        bp_name = resource_cls.blueprint and resource_cls.blueprint.name
        if subroute.bp_name and (not bp_name or bp_name != subroute.bp_name):
            from warnings import warn
            warn(f'Warning: overriding subresource blueprint '
                 f'{subroute.bp_name!r} with {bp_name!r}')
        subroute.blueprint = resource_cls.blueprint

        subroute.rule = resource_cls.subresource_route_rule(subroute)
        yield subroute

    resource_cls.url_prefix = resource_url_prefix


def reduce_routes(routes: Iterable[Union[Route, RouteGenerator]],
                  ) -> RouteGenerator:
    if not routes:
        raise StopIteration

    try:
        for route in routes:
            if isinstance(route, Route):
                yield route
            else:
                yield from reduce_routes(route)
    except TypeError as e:
        print(str(e), routes)


def rule(rule: str,
         cls_method_name_or_view_fn: Optional[Union[str, Callable]] = None,
         *,
         defaults: Optional[Defaults] = _missing,
         endpoint: Optional[str] = _missing,
         is_member: Optional[bool] = _missing,
         methods: Optional[Methods] = _missing,
         only_if: Optional[Union[bool, Callable[[Flask], bool]]] = _missing,
         **rule_options,
         ) -> RouteGenerator:
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
    is_controller = (inspect.isclass(controller_cls)
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
    if inspect.isclass(resource_cls) and issubclass(resource_cls, Resource):
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
                                 ) -> RouteGenerator:
    for route in reduce_routes(rules):
        route = route.copy()
        route.blueprint = controller_cls.blueprint
        route._controller_name = controller_cls.__name__
        route.view_func = controller_cls.method_as_view(route.method_name)
        route.rule = controller_cls.route_rule(route)
        yield route
