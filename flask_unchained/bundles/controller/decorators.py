from .attr_constants import FN_ROUTES_ATTR, NO_ROUTES_ATTR
from .route import Route


def route(rule=None, blueprint=None, defaults=None, endpoint=None,
          is_member=False, methods=None, only_if=None, **rule_options):
    def wrapper(fn):
        fn_routes = getattr(fn, FN_ROUTES_ATTR, [])
        route = Route(rule, fn, blueprint=blueprint, defaults=defaults,
                      endpoint=endpoint, is_member=is_member, methods=methods,
                      only_if=only_if, **rule_options)
        setattr(fn, FN_ROUTES_ATTR, fn_routes + [route])
        return fn

    if callable(rule):
        fn = rule
        rule = None
        return wrapper(fn)
    return wrapper


def no_route(arg=None):
    def wrapper(fn):
        setattr(fn, NO_ROUTES_ATTR, True)
        return fn

    if callable(arg):
        return wrapper(arg)
    return wrapper
