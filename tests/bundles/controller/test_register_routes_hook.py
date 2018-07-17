import pytest
from types import GeneratorType

from flask_unchained.bundles.controller.hooks import RegisterRoutesHook, Store
from flask_unchained.unchained import Unchained

from .fixtures.app_bundle import AppBundle
from .fixtures.auto_route_app_bundle import AutoRouteAppBundle
from .fixtures.vendor_bundle import VendorBundle
from .fixtures.empty_bundle import EmptyBundle


@pytest.fixture
def hook():
    unchained = Unchained()
    bundle_store = Store()
    return RegisterRoutesHook(unchained, bundle_store)


class TestRegisterRoutesHook:
    def test_get_explicit_routes(self, hook):
        routes = hook.get_explicit_routes(AppBundle)
        assert len(routes) == 4
        for route in routes:
            assert isinstance(route, GeneratorType)

        with pytest.raises(AttributeError) as e:
            hook.get_explicit_routes(EmptyBundle)
        assert 'Could not find a variable named `routes`' in str(e)

    def test_run_hook_with_explicit_routes(self, app, hook):
        with app.test_request_context():
            hook.run_hook(app, [VendorBundle, AppBundle])

            expected = {'one.view_one': 'view_one rendered',
                         'two.view_two': 'view_two rendered',
                         'three.view_three': 'view_three rendered',
                         'four.view_four': 'view_four rendered'}

            # check endpoints added to store
            assert list(hook.store.endpoints.keys()) == list(expected.keys())
            for endpoint in expected:
                route = hook.store.endpoints[endpoint]
                assert route.view_func() == expected[endpoint]

            # check endpoints registered with app
            assert set(app.view_functions.keys()) == set(expected.keys())
            for endpoint in expected:
                view_func = app.view_functions[endpoint]
                assert view_func() == expected[endpoint]

    def test_run_hook_with_implicit_routes(self, app, hook):
        with app.test_request_context():
            hook.run_hook(app, [VendorBundle, AutoRouteAppBundle])

            expected = {'site_controller.index': 'index rendered',
                        'site_controller.about': 'about rendered',
                        'views.view_one': 'view_one rendered',
                        'views.view_two': 'view_two rendered',
                        'three.view_three': 'view_three rendered',
                        'four.view_four': 'view_four rendered'}

            # check endpoints added to store
            assert list(hook.store.endpoints.keys()) == list(expected.keys())
            for endpoint in expected:
                route = hook.store.endpoints[endpoint]
                assert route.view_func() == expected[endpoint]

            # check endpoints registered with app
            assert set(app.view_functions.keys()) == set(expected.keys())
            for endpoint in expected:
                view_func = app.view_functions[endpoint]
                assert view_func() == expected[endpoint]
