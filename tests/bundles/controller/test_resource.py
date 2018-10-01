from flask_unchained.bundles.controller import Resource, route
from flask_unchained.bundles.controller.attr_constants import CONTROLLER_ROUTES_ATTR
from flask_unchained.bundles.controller.constants import ALL_METHODS
from flask_unchained.bundles.controller.utils import join


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
        assert DefaultResource.Meta.url_prefix == '/defaults'
        assert DefaultResource.Meta.member_param == '<int:id>'

    def test_custom_attributes(self):
        class FooResource(Resource):
            class Meta:
                url_prefix = '/foobars'
                member_param = '<string:slug>'

        assert FooResource.Meta.url_prefix == '/foobars'
        assert FooResource.Meta.member_param == '<string:slug>'

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
        class UserResource(Resource):
            def create(self):
                return self.redirect('get', id=1)

            def get(self, id):
                pass

        with app.test_request_context():
            for method_name, routes in getattr(UserResource,
                                               CONTROLLER_ROUTES_ATTR).items():
                for route in routes:
                    app.add_url_rule(
                        join(UserResource.Meta.url_prefix, route.full_rule),
                        view_func=UserResource.method_as_view(method_name),
                        endpoint=route.endpoint)

            resource = UserResource()
            resp = resource.create()
            assert resp.status_code == 302
            assert resp.location == '/users/1'

    def test_it_adds_route_to_extra_view_methods(self):
        routes = getattr(DefaultResource, CONTROLLER_ROUTES_ATTR)
        assert 'extra' in routes
