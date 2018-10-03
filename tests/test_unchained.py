import pytest

from flask_unchained.constants import DEV
from flask_unchained.unchained import Unchained

from ._bundles.empty_bundle import EmptyBundle
from ._bundles.myapp import MyAppBundle
from ._bundles.vendor_bundle import VendorBundle, awesome


class FakeApp:
    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        return rule, endpoint, view_func, options

    def before_request(self, fn):
        return fn('app')

    def before_first_request(self, fn):
        return fn('app')

    def after_request(self, fn):
        return fn('app')

    def teardown_request(self, fn):
        return fn('app')

    def teardown_appcontext(self, fn):
        return fn('app')

    def context_processor(self, fn):
        return fn('app')

    def shell_context_processor(self, fn):
        return fn('app')

    def url_defaults(self, fn):
        return fn('app')

    def url_value_preprocessor(self, fn):
        return fn('app')

    def errorhandler(self, fn):
        return fn('app')

    def register_error_handler(self, code_or_exception, fn):
        return fn('app')


class FakeBlueprint:
    def before_request(self, fn):
        return fn('bp')

    def after_request(self, fn):
        return fn('bp')

    def teardown_request(self, fn):
        return fn('bp')

    def context_processor(self, fn):
        return fn('bp')

    def url_defaults(self, fn):
        return fn('bp')

    def url_value_preprocessor(self, fn):
        return fn('bp')

    def errorhandler(self, fn):
        return fn('bp')

    def register_error_handler(self, code_or_exception, fn):
        return fn('bp')


class TestUnchained:
    def test_unchained(self, app):
        unchained = Unchained()
        app.unchained = unchained
        unchained.init_app(app, DEV, [VendorBundle(), MyAppBundle()])
        assert 'unchained' in app.extensions
        assert app.extensions['unchained'] == unchained

        with pytest.raises(AttributeError):
            fail = unchained.app

        assert isinstance(unchained.vendor_bundle, VendorBundle)
        assert unchained.extensions.awesome == awesome

    def test_deferred_functions(self, app):
        unchained = Unchained()
        fake_app = FakeApp()
        unchained.add_url_rule('/test', 'test.endpoint', 'view_func', methods=['GET'])
        unchained.before_request(lambda app: 'before_request')
        unchained.before_first_request(lambda app: 'before_first_request')
        unchained.after_request(lambda app: 'after_request')
        unchained.teardown_request(lambda app: 'teardown_request')
        unchained.teardown_appcontext(lambda app: 'teardown_appcontext')
        unchained.context_processor(lambda app: 'context_processor')
        unchained.shell_context_processor(lambda app: 'shell_context_processor')
        unchained.url_defaults(lambda app: 'url_defaults')
        unchained.url_value_preprocessor(lambda app: 'url_value_preprocessor')
        unchained.errorhandler(500)(lambda app: 'errorhandler')
        unchained.init_app(app, DEV)
        assert unchained._deferred_functions[0](fake_app) == (
            '/test', 'test.endpoint', 'view_func', {'methods': ['GET']})
        assert unchained._deferred_functions[1](fake_app) == 'before_request'
        assert unchained._deferred_functions[2](fake_app) == 'before_first_request'
        assert unchained._deferred_functions[3](fake_app) == 'after_request'
        assert unchained._deferred_functions[4](fake_app) == 'teardown_request'
        assert unchained._deferred_functions[5](fake_app) == 'teardown_appcontext'
        assert unchained._deferred_functions[6](fake_app) == 'context_processor'
        assert unchained._deferred_functions[7](fake_app) == 'shell_context_processor'
        assert unchained._deferred_functions[8](fake_app) == 'url_defaults'
        assert unchained._deferred_functions[9](fake_app) == 'url_value_preprocessor'
        assert unchained._deferred_functions[10](fake_app) == 'errorhandler'

    def test_deferred_bundle_functions(self, app):
        unchained = Unchained()
        empty = EmptyBundle()
        fake_bp = FakeBlueprint()
        unchained.empty_bundle.before_request(lambda bp: 'before_request')
        unchained.empty_bundle.after_request(lambda bp: 'after_request')
        unchained.empty_bundle.teardown_request(lambda bp: 'teardown_request')
        unchained.empty_bundle.context_processor(lambda bp: 'context_processor')
        unchained.empty_bundle.url_defaults(lambda bp: 'url_defaults')
        unchained.empty_bundle.url_value_preprocessor(lambda bp: 'url_value_preprocessor')
        unchained.empty_bundle.errorhandler(500)(lambda bp: 'errorhandler')
        unchained.init_app(app, DEV, [empty])
        assert empty._deferred_functions[0](fake_bp) == 'before_request'
        assert empty._deferred_functions[1](fake_bp) == 'after_request'
        assert empty._deferred_functions[2](fake_bp) == 'teardown_request'
        assert empty._deferred_functions[3](fake_bp) == 'context_processor'
        assert empty._deferred_functions[4](fake_bp) == 'url_defaults'
        assert empty._deferred_functions[5](fake_bp) == 'url_value_preprocessor'
        assert empty._deferred_functions[6](fake_bp) == 'errorhandler'
