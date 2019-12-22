import importlib
import inspect
import itertools

from flask_unchained import AppFactoryHook, Bundle, FlaskUnchained
from typing import *
from werkzeug.local import LocalProxy

from ..attr_constants import CONTROLLER_ROUTES_ATTR, FN_ROUTES_ATTR
from ..route import Route
from ..routes import _reduce_routes, _normalize_controller_routes, include


class RegisterRoutesHook(AppFactoryHook):
    """
    Registers routes.
    """

    name = 'routes'
    bundle_module_name = 'routes'
    require_exactly_one_bundle_module = True
    run_before = ['blueprints', 'bundle_blueprints']

    def run_hook(self, app: FlaskUnchained, bundles: List[Bundle]):
        app_bundle = bundles[-1]

        try:
            self.import_bundle_modules(app_bundle)[0]
        except IndexError:
            routes = self.collect_from_bundle(app_bundle)
        else:
            try:
                routes = self.get_explicit_routes(app_bundle)
            except AttributeError as e:
                if not app_bundle.is_single_module:
                    raise e
                routes = self.collect_from_bundle(app_bundle)

        self.process_objects(app, routes)

    def process_objects(self, app: FlaskUnchained, routes: Iterable[Route]):
        for route in _reduce_routes(routes):
            if route.should_register(app):
                if route.module_name and route in self.bundle.endpoints[route.endpoint]:
                    import warnings
                    warnings.warn(f'Duplicate route found: {route}')
                    continue

                self.bundle.endpoints[route.endpoint].append(route)
                if route._controller_cls:
                    key = f'{route._controller_cls.__name__}.{route.method_name}'
                    self.bundle.controller_endpoints[key].append(route)

        # build up a list of bundles with views:
        bundle_module_names = []  # [tuple(top_bundle_module_name, hierarchy_module_names)]
        for bundle in app.unchained.bundles.values():
            hierarchy = [bundle_super.module_name
                         for bundle_super in bundle._iter_class_hierarchy()
                         if bundle_super._has_views]
            if hierarchy:
                bundle_module_names.append((bundle.module_name, hierarchy))

        # for each route, figure out which bundle hierarchy it's from, and assign the
        # route to the top bundle for that hierarchy
        bundle_route_endpoints = set()
        for endpoint, endpoint_routes in self.bundle.endpoints.items():
            for route in endpoint_routes:
                if not route.module_name:
                    continue

                # FIXME would be nice for routes to know which bundle they're from...
                for top_level_bundle_module_name, hierarchy in bundle_module_names:
                    for bundle_module_name in hierarchy:
                        if route.module_name.startswith(bundle_module_name):
                            self.bundle.bundle_routes[
                                top_level_bundle_module_name
                            ].append(route)
                            bundle_route_endpoints.add(endpoint)
                            break

        # get all the remaining routes not belonging to a bundle
        self.bundle.other_routes = itertools.chain.from_iterable([
            routes for endpoint, routes
            in self.bundle.endpoints.items()
            if endpoint not in bundle_route_endpoints
        ])

        # we register non-bundle routes with the app here, and
        # the RegisterBundleBlueprintsHook registers the bundle routes
        for route in self.bundle.other_routes:
            app.add_url_rule(route.full_rule,
                             defaults=route.defaults,
                             endpoint=route.endpoint,
                             methods=route.methods,
                             view_func=route.view_func,
                             **route.rule_options)

    def get_explicit_routes(self, bundle: Bundle):
        routes_module = self.import_bundle_modules(bundle)[0]
        try:
            return getattr(routes_module, 'routes')()
        except AttributeError:
            module_name = self.get_module_names(bundle)[0]
            raise AttributeError(f'Could not find a variable named `routes` '
                                 f'in the {module_name} module!')

    def collect_from_bundle(self, bundle: Bundle):
        if not bundle._has_views:
            return ()

        from flask_unchained.hooks.views_hook import ViewsHook
        for views_module in ViewsHook.import_bundle_modules(bundle):
            for _, obj in inspect.getmembers(views_module, self.type_check):
                if hasattr(obj, FN_ROUTES_ATTR):
                    yield getattr(obj, FN_ROUTES_ATTR)
                else:
                    routes = getattr(obj, CONTROLLER_ROUTES_ATTR).values()
                    yield from _normalize_controller_routes(routes, obj)

            try:
                yield from include(views_module.__name__)
            except AttributeError:
                return ()

    def type_check(self, obj):
        if isinstance(obj, LocalProxy):
            return False
        is_controller = hasattr(obj, CONTROLLER_ROUTES_ATTR)
        is_view_fn = hasattr(obj, FN_ROUTES_ATTR)
        return is_controller or is_view_fn
