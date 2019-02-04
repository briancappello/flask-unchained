from flask_unchained.bundles.controller.routes import _reduce_routes

from .fixtures import routes as test_routes


EXPECTED_RESULTS = [
    ('site_controller.index', '/', ['GET']),
    ('site_controller.about', '/about', ['GET']),
    ('site_controller.terms', '/terms', ['GET']),
    ('site_controller.foobar', '/foobar', ['GET']),
    ('user_resource.list', '/users/', ['GET']),
    ('user_resource.create', '/users/', ['POST']),
    ('user_resource.get', '/users/<int:id>', ['GET']),
    ('user_resource.put', '/users/<int:id>', ['PUT']),
    ('user_resource.patch', '/users/<int:id>', ['PATCH']),
    ('user_resource.delete', '/users/<int:id>', ['DELETE']),
    ('user_resource.foobar', '/users/foobar', ['GET']),  # FIXME?
    ('role_resource.list', '/users/<int:user_id>/roles/', ['GET']),
    ('role_resource.create', '/users/<int:user_id>/roles/', ['POST']),
    ('role_resource.get', '/users/<int:user_id>/roles/<int:id>', ['GET']),
    ('role_resource.put', '/users/<int:user_id>/roles/<int:id>', ['PUT']),
    ('role_resource.patch', '/users/<int:user_id>/roles/<int:id>', ['PATCH']),
    ('role_resource.delete', '/users/<int:user_id>/roles/<int:id>', ['DELETE']),
    ('product_controller.index', '/products/', ['GET']),
    ('product_controller.good', '/products/good', ['GET']),
    ('product_controller.better', '/products/better', ['GET']),
    ('product_controller.best', '/products/best', ['GET']),
    ('views.simple', '/simple', ['GET']),
    ('views.one', '/one', ['GET']),
    ('views.two', '/two', ['GET']),
    ('views.three', '/three', ['GET', 'POST']),
]

EXPECTED_DEEP_RESULTS = [
    ('site_controller.index', '/app/site/', ['GET']),
    ('site_controller.about', '/app/site/about', ['GET']),
    ('site_controller.terms', '/app/site/terms', ['GET']),
    ('site_controller.foobar', '/app/site/foobar', ['GET']),
    ('user_resource.list', '/app/pre/users/', ['GET']),
    ('user_resource.create', '/app/pre/users/', ['POST']),
    ('user_resource.get', '/app/pre/users/<int:id>', ['GET']),
    ('user_resource.put', '/app/pre/users/<int:id>', ['PUT']),
    ('user_resource.patch', '/app/pre/users/<int:id>', ['PATCH']),
    ('user_resource.delete', '/app/pre/users/<int:id>', ['DELETE']),
    ('user_resource.foobar', '/app/pre/users/foobar', ['GET']),  # FIXME?
    ('role_resource.list', '/app/pre/users/<int:user_id>/roles/', ['GET']),
    ('role_resource.create', '/app/pre/users/<int:user_id>/roles/', ['POST']),
    ('role_resource.get', '/app/pre/users/<int:user_id>/roles/<int:id>', ['GET']),
    ('role_resource.put', '/app/pre/users/<int:user_id>/roles/<int:id>', ['PUT']),
    ('role_resource.patch', '/app/pre/users/<int:user_id>/roles/<int:id>', ['PATCH']),
    ('role_resource.delete', '/app/pre/users/<int:user_id>/roles/<int:id>', ['DELETE']),
    ('views.simple', '/app/pre/users/<int:user_id>/roles/<int:role_id>/simple', ['GET']),
    ('another_resource.list', '/app/pre/users/<int:user_id>/roles/<int:role_id>/another/', ['GET']),
    ('another_resource.get', '/app/pre/users/<int:user_id>/roles/<int:role_id>/another/<int:id>', ['GET']),
    ('views.one', '/app/pre/users/<int:user_id>/roles/<int:role_id>/one', ['GET']),
    ('views.two', '/app/pre/users/<int:user_id>/roles/<int:role_id>/two', ['GET']),
    ('views.three', '/app/pre/users/<int:user_id>/roles/<int:role_id>/three', ['GET', 'POST']),
    ('views.one', '/app/pre/users/<int:user_id>/roles/<int:role_id>/deep/one', ['GET']),
    ('views.two', '/app/pre/users/<int:user_id>/roles/<int:role_id>/deep/two', ['GET']),
    ('views.three', '/app/pre/users/<int:user_id>/roles/<int:role_id>/deep/three', ['GET', 'POST']),
]


class TestReduceRoutes:
    def test_explicit_routes(self):
        routes = list(_reduce_routes(test_routes.explicit_routes()))
        for i, expected in enumerate(t for t in EXPECTED_RESULTS
                                     if 'foobar' not in t[0]):
            route = routes[i]
            assert route.endpoint == expected[0], (route.endpoint, expected[0])
            assert route.full_rule == expected[1], route.endpoint
            assert route.methods == expected[2], route.endpoint

    def test_implicit_routes(self):
        routes = list(_reduce_routes(test_routes.implicit_routes()))
        for i, expected in enumerate(EXPECTED_RESULTS):
            route = routes[i]
            assert route.endpoint == expected[0], route.endpoint
            assert route.full_rule == expected[1], route.endpoint
            assert route.methods == expected[2], route.endpoint

    def test_deep_routes(self):
        routes = list(_reduce_routes(test_routes.deep()))
        for i, expected in enumerate(EXPECTED_DEEP_RESULTS):
            route = routes[i]
            assert route.endpoint == expected[0], route.endpoint
            assert route.full_rule == expected[1], route.endpoint
            assert route.methods == expected[2], route.endpoint
