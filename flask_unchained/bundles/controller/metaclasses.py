from flask_unchained.di import set_up_class_dependency_injection
from flask_unchained.utils import deep_getattr
from types import FunctionType

from .attr_constants import (
    ABSTRACT_ATTR, CONTROLLER_ROUTES_ATTR, FN_ROUTES_ATTR, NO_ROUTES_ATTR,
    NOT_VIEWS_ATTR, REMOVE_SUFFIXES_ATTR)
from .constants import (
    ALL_METHODS, INDEX_METHODS, CREATE, DELETE, GET, LIST, PATCH, PUT)
from .route import Route


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
        - finish initializing Routes
    """
    def __new__(mcs, name, bases, clsdict):
        set_up_class_dependency_injection(name, clsdict)
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

            method_routes = getattr(method, FN_ROUTES_ATTR, [Route(None, method)])
            controller_routes[method_name] = method_routes

        setattr(cls, CONTROLLER_ROUTES_ATTR, controller_routes)
        return cls

    def __init__(cls, name, bases, clsdict):
        super().__init__(name, bases, clsdict)
        for routes in getattr(cls, CONTROLLER_ROUTES_ATTR, {}).values():
            for route in routes:
                route._controller_cls = cls


class ResourceMeta(ControllerMeta):
    """
    Metaclass for Resource class
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
            route = controller_routes.get(method_name)[0]
            rule = None
            if method_name in INDEX_METHODS:
                rule = '/'
            else:
                route._is_member_method = True
                route._member_param = deep_getattr(clsdict, bases, 'member_param')
            route.rule = rule
            controller_routes[method_name] = [route]
        setattr(cls, CONTROLLER_ROUTES_ATTR, controller_routes)

        return cls


def get_not_views(clsdict, bases):
    not_views = deep_getattr({}, bases, NOT_VIEWS_ATTR, [])
    return ({name for name, method in clsdict.items()
             if is_view_func(name, method)
             and not getattr(method, FN_ROUTES_ATTR, None)}.union(not_views))


def get_remove_suffixes(name, bases, extras):
    existing_suffixes = deep_getattr({}, bases, REMOVE_SUFFIXES_ATTR, [])
    new_suffixes = [name] + extras
    return ([suffix for suffix in new_suffixes
             if suffix not in existing_suffixes] + existing_suffixes)


def is_view_func(method_name, method):
    is_function = isinstance(method, FunctionType)
    is_private = method_name.startswith('_')
    has_no_routes = getattr(method, NO_ROUTES_ATTR, False)
    return is_function and not (is_private or has_no_routes)
