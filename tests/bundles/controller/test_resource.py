from flask_unchained.bundles.controller import Resource, route
from flask_unchained.bundles.controller.attr_constants import CONTROLLER_ROUTES_ATTR
from flask_unchained.bundles.controller.constants import ALL_METHODS


class DefaultResource(Resource):
    def list(self):
        pass

    def create(self):
        pass

    def get(self):
        pass

    def patch(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    def extra(self):
        pass


class TestResource:
    def test_default_attributes(self):
        assert DefaultResource.url_prefix == '/defaults'
        assert DefaultResource.member_param == '<int:id>'

    def test_custom_attributes(self):
        class FooResource(Resource):
            url_prefix = '/foobars'
            member_param = '<string:slug>'

        assert FooResource.url_prefix == '/foobars'
        assert FooResource.member_param == '<string:slug>'

    def test_method_as_view_assigns_correct_http_methods(self):
        for method_name in ALL_METHODS:
            view = DefaultResource.method_as_view(method_name)
            assert view.methods == DefaultResource.resource_methods[method_name]

        list = DefaultResource.method_as_view('list')
        assert list.methods == ['GET']

        create = DefaultResource.method_as_view('create')
        assert create.methods == ['POST']

        get = DefaultResource.method_as_view('get')
        assert get.methods == ['GET']

        patch = DefaultResource.method_as_view('patch')
        assert patch.methods == ['PATCH']

        put = DefaultResource.method_as_view('put')
        assert put.methods == ['PUT']

        delete = DefaultResource.method_as_view('delete')
        assert delete.methods == ['DELETE']

    def test_redirect_to_controller_method(self, app):
        class UserController(Resource):
            def create(self):
                return self.redirect('get', id=1)

            def get(self, id):
                pass

        with app.test_request_context():
            for method_name, routes in getattr(UserController,
                                               CONTROLLER_ROUTES_ATTR).items():
                for route in routes:
                    app.add_url_rule(
                        UserController.route_rule(route),
                        view_func=UserController.method_as_view(method_name),
                        endpoint=route.endpoint)

            controller = UserController()
            resp = controller.create()
            assert resp.status_code == 302
            assert resp.location == '/users/1'

    def test_it_adds_route_to_extra_view_methods(self):
        routes = getattr(DefaultResource, CONTROLLER_ROUTES_ATTR)
        assert 'extra' in routes

    def test_route_rule(self):
        class FooResource(Resource):
            def a(self):
                pass

            @route(is_member=True)
            def b(self):
                pass

        routes = getattr(FooResource, CONTROLLER_ROUTES_ATTR)
        assert FooResource.route_rule(routes['a'][0]) == '/foos/a'
        assert FooResource.route_rule(routes['b'][0]) == '/foos/<int:foo_id>/b'

    def test_route_rule_with_resource_methods(self):
        routes = getattr(DefaultResource, CONTROLLER_ROUTES_ATTR)
        assert DefaultResource.route_rule(routes['list'][0]) == '/defaults'
        assert DefaultResource.route_rule(routes['create'][0]) == '/defaults'
        assert DefaultResource.route_rule(routes['get'][0]) == '/defaults/<int:id>'
        assert DefaultResource.route_rule(routes['patch'][0]) == '/defaults/<int:id>'
        assert DefaultResource.route_rule(routes['put'][0]) == '/defaults/<int:id>'
        assert DefaultResource.route_rule(routes['delete'][0]) == '/defaults/<int:id>'
