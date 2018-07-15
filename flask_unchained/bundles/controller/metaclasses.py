from flask_unchained.di import setup_class_dependency_injection
from flask_unchained.utils import deep_getattr
from types import FunctionType

from .attr_constants import (
    ABSTRACT_ATTR, CONTROLLER_ROUTES_ATTR, FN_ROUTES_ATTR, NO_ROUTES_ATTR,
    NOT_VIEWS_ATTR, REMOVE_SUFFIXES_ATTR)
from .constants import (
    ALL_METHODS, INDEX_METHODS, CREATE, DELETE, GET, LIST, PATCH, PUT)
from .route import Route
from .utils import controller_name, join, get_param_tuples, method_name_to_url


CONTROLLER_REMOVE_EXTRA_SUFFIXES = ['View']
RESOURCE_REMOVE_EXTRA_SUFFIXES = ['MethodView']


class ControllerMeta(type):
    """
    Metaclass for Controller class

    Sets up automatic dependency injection and routes:
    - if base class, remember utility methods (NOT_VIEWS_ATTR)
    - if subclass of a base class, init CONTROLLER_ROUTES_ATTR
        - check if methods were decorated with @route, otherwise
          create a new Route for each method
        - finish initializing routes (set blueprint, _controller_name)
    """
    def __new__(mcs, name, bases, clsdict):
        setup_class_dependency_injection(name, clsdict)
        cls = super().__new__(mcs, name, bases, clsdict)

        if ABSTRACT_ATTR in clsdict:
            setattr(cls, NOT_VIEWS_ATTR, get_not_views(clsdict, bases))
            setattr(cls, REMOVE_SUFFIXES_ATTR, get_remove_suffixes(
                name, bases, CONTROLLER_REMOVE_EXTRA_SUFFIXES))
            return cls

        controller_routes = getattr(cls, CONTROLLER_ROUTES_ATTR, {}).copy()
        not_views = deep_getattr({}, bases, NOT_VIEWS_ATTR)

        for method_name, method in clsdict.items():
            if (method_name in not_views
                    or not is_view_func(method_name, method)):
                controller_routes.pop(method_name, None)
                continue

            method_routes = getattr(method, FN_ROUTES_ATTR,
                                    [Route(None, method)])
            for route in method_routes:
                route.blueprint = deep_getattr(clsdict, bases, 'blueprint')
                route._controller_name = name
            controller_routes[method_name] = method_routes

        setattr(cls, CONTROLLER_ROUTES_ATTR, controller_routes)
        return cls

    def route_rule(cls, route: Route):
        rule = route.rule
        if not rule:
            rule = method_name_to_url(route.method_name)
        return join(cls.url_prefix, rule)


class ResourceMeta(ControllerMeta):
    """
    Metaclass for Resource class

    Sets up special rules for RESTful behavior:
    - GET    '/' -> cls.list()
    - POST   '/' -> cls.create()
    - GET    '/<cls.member_param>' -> cls.get(<param_name>=<param_value>)
    - PATCH  '/<cls.member_param>' -> cls.patch(<param_name>=<param_value>)
    - PUT    '/<cls.member_param>' -> cls.put(<param_name>=<param_value>)
    - DELETE '/<cls.member_param>' -> cls.delete(<param_name>=<param_value>)
    """
    resource_methods = {LIST: ['GET'], CREATE: ['POST'],
                        GET: ['GET'], PATCH: ['PATCH'],
                        PUT: ['PUT'], DELETE: ['DELETE']}

    def __new__(mcs, name, bases, clsdict):
        cls = super().__new__(mcs, name, bases, clsdict)
        if ABSTRACT_ATTR in clsdict:
            setattr(cls, REMOVE_SUFFIXES_ATTR, get_remove_suffixes(
                name, bases, RESOURCE_REMOVE_EXTRA_SUFFIXES))
            return cls

        controller_routes = getattr(cls, CONTROLLER_ROUTES_ATTR)
        for method_name in ALL_METHODS:
            if not clsdict.get(method_name):
                continue

            if method_name in INDEX_METHODS:
                rule = '/'
            else:
                rule = deep_getattr(clsdict, bases, 'member_param')

            route = controller_routes.get(method_name)[0]
            route.rule = rule
            controller_routes[method_name] = [route]
        setattr(cls, CONTROLLER_ROUTES_ATTR, controller_routes)

        return cls

    def route_rule(cls, route: Route):
        rule = route.rule
        if not rule:
            rule = method_name_to_url(route.method_name)
        if route.is_member:
            rule = rename_parent_resource_param_name(
                cls, join(cls.member_param, rule))
        return join(cls.url_prefix, rule)

    def subresource_route_rule(cls, subresource_route: Route):
        rule = join(cls.url_prefix, cls.member_param, subresource_route.rule)
        return rename_parent_resource_param_name(cls, rule)


def get_not_views(clsdict, bases):
    not_views = deep_getattr({}, bases, NOT_VIEWS_ATTR, [])
    return ({name for name, method in clsdict.items()
             if is_view_func(name, method)
             and not getattr(method, FN_ROUTES_ATTR, None)}.union(not_views))


def get_remove_suffixes(name, bases, extras):
    existing_suffixes = deep_getattr({}, bases, REMOVE_SUFFIXES_ATTR, [])
    new_suffixes = [name] + extras
    return ([x for x in new_suffixes if x not in existing_suffixes]
            + existing_suffixes)


def is_view_func(method_name, method):
    is_function = isinstance(method, FunctionType)
    is_private = method_name.startswith('_')
    has_no_routes = getattr(method, NO_ROUTES_ATTR, False)
    return is_function and not (is_private or has_no_routes)


def rename_parent_resource_param_name(parent_cls, url_rule):
    type_, orig_name = get_param_tuples(parent_cls.member_param)[0]
    orig_param = f'<{type_}:{orig_name}>'
    renamed_param = f'<{type_}:{controller_name(parent_cls)}_{orig_name}>'
    return url_rule.replace(orig_param, renamed_param, 1)
