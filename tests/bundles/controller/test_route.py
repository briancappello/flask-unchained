import pytest

from flask_unchained.bundles.controller import Controller
from flask_unchained.bundles.controller.attr_constants import CONTROLLER_ROUTES_ATTR
from flask_unchained.bundles.controller.route import Route


class TestRoute:
    def test_should_register_defaults_to_true(self):
        route = Route('/path', lambda: 'view_func')
        assert route.should_register(None) is True

    def test_should_register_with_boolean(self):
        route = Route('/path', lambda: 'view_func', only_if=True)
        assert route.should_register(None) is True

    def test_should_register_with_callable(self):
        route = Route('/path', lambda: 'view_func', only_if=lambda x: x)
        assert route.should_register(True) is True
        assert route.should_register(False) is False

    def test_full_name_with_controller(self):
        class SomeController(Controller):
            def index(self):
                pass

        route = getattr(SomeController, CONTROLLER_ROUTES_ATTR)['index'][0]
        assert route.full_name == \
               'tests.bundles.controller.test_route.SomeController.index'

    def test_full_name_with_func(self):
        def a_view():
            pass

        route = Route('/foo', a_view)
        assert route.full_name == 'tests.bundles.controller.test_route.a_view'
