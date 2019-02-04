import pytest

from flask import Blueprint

from flask_unchained.bundles.controller import Controller, Resource
from flask_unchained.bundles.controller.attr_constants import (
    CONTROLLER_ROUTES_ATTR, FN_ROUTES_ATTR)
from flask_unchained.bundles.controller.decorators import route as route_decorator
from flask_unchained.bundles.controller.routes import (
    controller, func, include, resource, _normalize_args)


bp = Blueprint('test', __name__)
bp2 = Blueprint('test2', __name__)


def undecorated_view():
    pass


@route_decorator
def decorated_view():
    pass


@route_decorator('/first', endpoint='first')
@route_decorator('/second', endpoint='second')
def multi_route_view():
    pass


@route_decorator(endpoint='default')
@route_decorator('/first', endpoint='first')
@route_decorator('/second', endpoint='second')
def implicit_multi_route_view():
    pass


class SiteController(Controller):
    @route_decorator('/')
    def index(self):
        pass

    def about(self):
        pass


class UserResource(Resource):
    def list(self):
        pass

    def get(self, id):
        pass


class RoleResource(Resource):
    def list(self):
        pass

    def get(self, id):
        pass


class FooResource(Resource):
    def list(self):
        pass

    def get(self, id):
        pass


class BarResource(Resource):
    def list(self):
        pass

    def get(self, id):
        pass


class BazResource(Resource):
    class Meta:
        unique_member_param = '<string:baz>'

    def list(self):
        pass

    def get(self, id):
        pass


class MultiRouteController(Controller):
    @route_decorator('/hello/', defaults=dict(param='DEFAULT'))
    @route_decorator('/hello/<string:param>/')
    def hello(self, param):
        return param


class TestMultiRouteController:
    def test_it_works(self):
        routes = list(controller(MultiRouteController))
        assert routes[0].full_rule == '/hello/<string:param>/'
        assert routes[0].endpoint == 'multi_route_controller.hello'
        assert not routes[0].defaults

        assert routes[1].rule == '/hello/'
        assert routes[1].endpoint == 'multi_route_controller.hello'
        assert routes[1].defaults == dict(param='DEFAULT')


class TestController:
    def test_it_works_with_only_a_controller_cls(self):
        routes = list(controller(SiteController))
        assert len(routes) == 2
        assert routes[0].endpoint == 'site_controller.index'
        assert routes[0].rule == '/'
        assert routes[1].endpoint == 'site_controller.about'
        assert routes[1].rule == '/about'

    def test_it_works_with_a_prefix_and_controller_cls(self):
        routes = list(controller('/prefix', SiteController))
        assert len(routes) == 2
        assert routes[0].endpoint == 'site_controller.index'
        assert routes[0].rule == '/prefix/'
        assert routes[1].endpoint == 'site_controller.about'
        assert routes[1].rule == '/prefix/about'

    def test_it_requires_a_controller_cls(self):
        with pytest.raises(ValueError):
            list(controller('/fail'))

        with pytest.raises(ValueError):
            list(controller('/fail', None))

        with pytest.raises(ValueError):
            list(controller(None))

        with pytest.raises(ValueError):
            list(controller(None, SiteController))

        with pytest.raises(TypeError):
            list(controller(UserResource))

        with pytest.raises(TypeError):
            list(controller('/users', UserResource))

    def test_it_does_not_mutate_existing_routes(self):
        routes = list(controller('/prefix', SiteController))
        orig_routes = [route
                       for routes in getattr(SiteController,
                                             CONTROLLER_ROUTES_ATTR).values()
                       for route in routes]
        assert orig_routes[0].endpoint == routes[0].endpoint
        assert orig_routes[0].rule == '/'
        assert routes[0].rule == '/prefix/'


class TestFunc:
    def test_it_works_with_undecorated_view(self):
        route = list(func(undecorated_view))[0]
        assert route.view_func == undecorated_view
        assert route.rule == '/undecorated-view'
        assert route.blueprint is None
        assert route.endpoint == 'tests.bundles.controller.test_routes.undecorated_view'
        assert route.defaults == {}
        assert route.methods == ['GET']
        assert route.only_if is True

    def test_override_rule_options_with_undecorated_view(self):
        route = list(func('/a/<id>', undecorated_view, blueprint=bp,
                          endpoint='overridden.endpoint',
                          defaults={'id': 1}, methods=['GET', 'POST'],
                          only_if='only_if'))[0]
        assert route.rule == '/a/<id>'
        assert route.view_func == undecorated_view
        assert route.blueprint == bp
        assert route.endpoint == 'overridden.endpoint'
        assert route.defaults == {'id': 1}
        assert route.methods == ['GET', 'POST']
        assert route.only_if is 'only_if'

    def test_it_works_with_decorated_view(self):
        route = list(func(decorated_view))[0]
        assert route.view_func == decorated_view
        assert route.rule == '/decorated-view'
        assert route.blueprint is None
        assert route.endpoint == 'tests.bundles.controller.test_routes.decorated_view'
        assert route.defaults == {}
        assert route.methods == ['GET']
        assert route.only_if is None

    def test_override_rule_options_with_decorated_view(self):
        route = list(func('/b/<id>', decorated_view, blueprint=bp,
                          endpoint='overridden.endpoint',
                          defaults={'id': 1}, methods=['GET', 'POST'],
                          only_if='only_if'))[0]
        assert route.rule == '/b/<id>'
        assert route.view_func == decorated_view
        assert route.blueprint == bp
        assert route.endpoint == 'overridden.endpoint'
        assert route.defaults == {'id': 1}
        assert route.methods == ['GET', 'POST']
        assert route.only_if == 'only_if'

    def test_it_requires_a_callable(self):
        with pytest.raises(ValueError):
            list(func('/fail'))

        with pytest.raises(ValueError):
            list(func('/fail', None))

        with pytest.raises(ValueError):
            list(func(None))

        with pytest.raises(ValueError):
            list(func(None, undecorated_view))

    def test_it_makes_new_route_if_decorated_with_multiple_other_routes(self):
        route = list(func(multi_route_view))[0]
        assert route.endpoint == 'tests.bundles.controller.test_routes.multi_route_view'

    def test_it_reuses_route_if_url_matches_a_decorated_route(self):
        route = list(func('/first', multi_route_view, methods=['PUT']))[0]
        assert route.methods == ['PUT']
        assert route.endpoint == 'first'

    def test_it_reuses_route_url_implicitly_matches(self):
        route = list(func(implicit_multi_route_view))[0]
        assert route.endpoint == 'default'

    def test_it_does_not_mutate_existing_routes(self):
        route = list(func('/foo', decorated_view))[0]
        orig_route = getattr(decorated_view, FN_ROUTES_ATTR)[0]
        assert orig_route.endpoint == route.endpoint
        assert orig_route.rule == '/decorated-view'
        assert route.rule == '/foo'


class TestInclude:
    def test_it_raises_if_no_routes_found(self):
        with pytest.raises(ImportError):
            # trying to import this.should.fail prints the zen of python!
            list(include('should.not.exist'))

        with pytest.raises(AttributeError):
            list(include('tests.bundles.controller.fixtures.routes'))

        with pytest.raises(AttributeError):
            list(include('tests.bundles.controller.fixtures.routes', attr='fail'))

    def test_it_only_includes_only(self):
        routes = list(include('tests.bundles.controller.fixtures.other_routes',
                              only=['views.one']))
        assert len(routes) == 1
        assert routes[0].endpoint == 'views.one'

    def test_it_does_not_include_excludes(self):
        routes = list(include('tests.bundles.controller.fixtures.other_routes',
                              exclude=['views.three']))
        assert len(routes) == 2
        assert routes[0].endpoint == 'views.one'
        assert routes[1].endpoint == 'views.two'


class TestResource:
    def test_it_works_with_only_resource(self):
        routes = list(resource(UserResource))
        assert len(routes) == 2
        assert routes[0].endpoint == 'user_resource.list'
        assert routes[0].rule == '/users/'
        assert routes[1].endpoint == 'user_resource.get'
        assert routes[1].rule == '/users/<int:id>'

    def test_it_works_with_a_prefix(self):
        routes = list(resource('/prefix', UserResource))
        assert len(routes) == 2
        assert routes[0].endpoint == 'user_resource.list'
        assert routes[0].rule == '/prefix/'
        assert routes[1].endpoint == 'user_resource.get'
        assert routes[1].rule == '/prefix/<int:id>'

    def test_it_works_with_a_customized_member_param(self):
        routes = list(resource(UserResource, member_param='<string:slug>'))
        assert len(routes) == 2
        assert routes[0].endpoint == 'user_resource.list'
        assert routes[0].rule == '/users/'
        assert routes[1].endpoint == 'user_resource.get'
        assert routes[1].rule == '/users/<string:slug>'

    def test_it_works_with_automatic_unique_member_params(self):
        routes = list(resource('/foo', FooResource, subresources=[
            resource(BarResource),
        ]))
        assert routes[0].endpoint == 'foo_resource.list'
        assert routes[0].rule == '/foo/'
        assert routes[1].endpoint == 'foo_resource.get'
        assert routes[1].rule == '/foo/<int:id>'
        assert routes[2].endpoint == 'bar_resource.list'
        assert routes[2].rule == '/foo/<int:foo_id>/bars/'
        assert routes[3].endpoint == 'bar_resource.get'
        assert routes[3].rule == '/foo/<int:foo_id>/bars/<int:id>'

    def test_it_renames_with_deeply_customized_member_params(self):
        routes = list(resource(UserResource,
                               member_param='<string:slug>',
                               subresources=[resource(RoleResource,
                                                      member_param='<string:slug>')]))

        assert routes[0].endpoint == 'user_resource.list'
        assert routes[0].rule == '/users/'
        assert routes[1].endpoint == 'user_resource.get'
        assert routes[1].rule == '/users/<string:slug>'
        assert routes[2].endpoint == 'role_resource.list'
        assert routes[2].rule == '/users/<string:user_slug>/roles/'
        assert routes[3].endpoint == 'role_resource.get'
        assert routes[3].rule == '/users/<string:user_slug>/roles/<string:slug>'

    def test_it_renames_with_deeply_customized_unique_member_params(self):
        routes = list(resource('/baz', BazResource,
                               subresources=[resource(BarResource)]))

        assert routes[0].endpoint == 'baz_resource.list'
        assert routes[0].rule == '/baz/'
        assert routes[1].endpoint == 'baz_resource.get'
        assert routes[1].rule == '/baz/<int:id>'
        assert routes[2].endpoint == 'bar_resource.list'
        assert routes[2].rule == '/baz/<string:baz>/bars/'
        assert routes[3].endpoint == 'bar_resource.get'
        assert routes[3].rule == '/baz/<string:baz>/bars/<int:id>'

    def test_member_param_overrides_unique_member_params(self):
        routes = list(resource('/baz', BazResource, unique_member_param='<int:pk>',
                               subresources=[
                                   resource(BarResource, member_param='<int:pk>')]))

        assert routes[0].endpoint == 'baz_resource.list'
        assert routes[0].rule == '/baz/'
        assert routes[1].endpoint == 'baz_resource.get'
        assert routes[1].rule == '/baz/<int:id>'
        assert routes[2].endpoint == 'bar_resource.list'
        assert routes[2].rule == '/baz/<int:pk>/bars/'
        assert routes[3].endpoint == 'bar_resource.get'
        assert routes[3].rule == '/baz/<int:baz_pk>/bars/<int:pk>'

    def test_differently_named_deeply_customized_member_params(self):
        routes = list(resource(UserResource,
                               member_param='<string:slug>',
                               subresources=[resource(RoleResource,
                                                      member_param='<string:slug2>')]))

        assert routes[0].endpoint == 'user_resource.list'
        assert routes[0].rule == '/users/'
        assert routes[1].endpoint == 'user_resource.get'
        assert routes[1].rule == '/users/<string:slug>'
        assert routes[2].endpoint == 'role_resource.list'
        assert routes[2].rule == '/users/<string:user_slug>/roles/'
        assert routes[3].endpoint == 'role_resource.get'
        assert routes[3].rule == '/users/<string:user_slug>/roles/<string:slug2>'

    def test_similarly_named_deeply_customized_member_params(self):
        routes = list(resource(
            UserResource, member_param='<string:slug>', subresources=[
                resource(RoleResource, member_param='<int:id>', subresources=[
                    resource(FooResource, member_param='<string:slug>', subresources=[
                        resource(BarResource, member_param='<int:id>')
                    ])
                ])
            ]))

        assert routes[0].endpoint == 'user_resource.list'
        assert routes[0].rule == '/users/'
        assert routes[1].endpoint == 'user_resource.get'
        assert routes[1].rule == routes[0].rule + '<string:slug>'
        assert routes[2].endpoint == 'role_resource.list'
        assert routes[2].rule == '/users/<string:user_slug>/roles/'
        assert routes[3].endpoint == 'role_resource.get'
        assert routes[3].rule == routes[2].rule + '<int:id>'
        assert routes[4].endpoint == 'foo_resource.list'
        assert routes[4].rule == '/users/<string:user_slug>/roles/<int:role_id>/foos/'
        assert routes[5].endpoint == 'foo_resource.get'
        assert routes[5].rule == routes[4].rule + '<string:slug>'
        assert routes[6].endpoint == 'bar_resource.list'
        assert routes[6].rule == \
           '/users/<string:user_slug>/roles/<int:role_id>/foos/<string:foo_slug>/bars/'
        assert routes[7].endpoint == 'bar_resource.get'
        assert routes[7].rule == routes[6].rule + '<int:id>'

    def test_it_requires_a_controller(self):
        with pytest.raises(ValueError):
            list(resource('/fail'))

        with pytest.raises(ValueError):
            list(resource('/fail', None))

        with pytest.raises(ValueError):
            list(resource(None))

        with pytest.raises(ValueError):
            list(resource(None, UserResource))

    def test_it_does_not_mutate_existing_routes(self):
        routes = list(resource('/prefix', UserResource))
        orig_routes = [route
                       for routes in getattr(UserResource,
                                             CONTROLLER_ROUTES_ATTR).values()
                       for route in routes]
        assert orig_routes[0].endpoint == routes[0].endpoint
        assert orig_routes[0].rule == '/'
        assert routes[0].rule == '/prefix/'

    def test_it_does_not_mutate_subresource_routes(self):
        routes = list(resource('/one', UserResource, subresources=[
            resource('/two', RoleResource)
        ]))
        orig_routes = [route
                       for routes in getattr(RoleResource,
                                             CONTROLLER_ROUTES_ATTR).values()
                       for route in routes]
        assert orig_routes[0].endpoint == routes[2].endpoint
        assert orig_routes[1].endpoint == routes[3].endpoint

        assert orig_routes[0].rule == '/'
        assert orig_routes[1].rule == '/<int:id>'
        assert routes[2].rule == '/one/<int:user_id>/two/'
        assert routes[3].rule == '/one/<int:user_id>/two/<int:id>'


def test_normalize_args():
    def is_bp(maybe_bp, has_rule):
        return isinstance(maybe_bp, Blueprint)

    assert _normalize_args(bp, None, is_bp) == (None, bp)
    assert _normalize_args('str', bp, is_bp) == ('str', bp)

    # this use case makes no sense, but it completes coverage
    assert _normalize_args(None, 'str', lambda *args, **kw: False) is None
    assert _normalize_args('str', None, lambda *args, **kw: False) is None
