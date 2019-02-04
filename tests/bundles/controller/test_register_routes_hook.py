import pytest

from flask_unchained.bundles.controller import ControllerBundle
from flask_unchained.bundles.controller.hooks import RegisterRoutesHook
from flask_unchained.bundles.controller.route import Route
from flask_unchained.bundles.controller.routes import _reduce_routes
from flask_unchained.unchained import Unchained

from .fixtures.app_bundle import AppBundle
from .fixtures.auto_route_app_bundle import AutoRouteAppBundle
from .fixtures.vendor_bundle import VendorBundle
from .fixtures.empty_bundle import EmptyBundle


@pytest.fixture
def hook(app):
    app.view_functions = {}
    unchained = Unchained()
    return RegisterRoutesHook(unchained, ControllerBundle())


class TestRegisterRoutesHook:
    def test_get_explicit_routes(self, app, hook: RegisterRoutesHook):
        hook.run_hook(app, [AppBundle()])
        discovered_routes = list(_reduce_routes(hook.get_explicit_routes(AppBundle())))
        assert len(discovered_routes) == 5
        for route in discovered_routes:
            assert isinstance(route, Route)

        registered_routes = hook.bundle.endpoints.values()
        assert len(registered_routes) == len(app.url_map._rules) == 4

        with pytest.raises(AttributeError) as e:
            hook.get_explicit_routes(EmptyBundle())
        assert 'Could not find a variable named `routes`' in str(e)

    def test_run_hook_with_explicit_routes(self, app, hook: RegisterRoutesHook):
        with app.test_request_context():
            hook.run_hook(app, [VendorBundle(), AppBundle()])

            expected = {'one.view_one': 'view_one rendered',
                        'two.view_two': 'view_two rendered',
                        'three.view_three': 'view_three rendered',
                        'four.view_four': 'view_four rendered'}

            # check endpoints added to store
            assert list(hook.bundle.endpoints.keys()) == list(expected.keys())
            for endpoint in expected:
                for route in hook.bundle.endpoints[endpoint]:
                    assert route.view_func() == expected[endpoint]

            # check endpoints registered with app
            assert set(app.view_functions.keys()) == set(expected.keys())
            for endpoint in expected:
                view_func = app.view_functions[endpoint]
                assert view_func() == expected[endpoint]

    def test_run_hook_with_implicit_routes(self, app, hook: RegisterRoutesHook):
        with app.test_request_context():
            hook.run_hook(app, [VendorBundle(), AutoRouteAppBundle()])

            expected = {'site_controller.index': 'index rendered',
                        'site_controller.about': 'about rendered',
                        'views.view_one': 'view_one rendered',
                        'views.view_two': 'view_two rendered',
                        'three.view_three': 'view_three rendered',
                        'four.view_four': 'view_four rendered'}

            # check endpoints added to store
            assert list(hook.bundle.endpoints.keys()) == list(expected.keys())
            for endpoint in expected:
                for route in hook.bundle.endpoints[endpoint]:
                    assert route.view_func() == expected[endpoint]

            # check endpoints registered with app
            assert set(app.view_functions.keys()) == set(expected.keys())
            for endpoint in expected:
                view_func = app.view_functions[endpoint]
                assert view_func() == expected[endpoint]
