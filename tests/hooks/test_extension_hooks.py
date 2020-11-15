import pytest

from flask_unchained.hooks import InitExtensionsHook, RegisterExtensionsHook
from flask_unchained.unchained import Unchained

from .._bundles.myapp import MyAppBundle, myext
from .._bundles.empty_bundle import EmptyBundle
from .._bundles.vendor_bundle import VendorBundle, awesome


class FakeExt:
    def __init__(self, name):
        self.app = None
        self.name = name

    def init_app(self, app):
        self.app = app


FAKE_EXTENSIONS = {
    'one': (FakeExt('one'), ['two', 'three']),
    'two': (FakeExt('two'), ['four']),
    'three': (FakeExt('three'), ['four']),
    'four': FakeExt('four'),
}


@pytest.fixture
def register_hook():
    return RegisterExtensionsHook(Unchained())


@pytest.fixture
def init_hook():
    return InitExtensionsHook(Unchained())


class TestRegisterExtensionsHook:
    def test_collect_from_bundle(self, register_hook: RegisterExtensionsHook):
        assert register_hook.collect_from_bundle(EmptyBundle()) == {}

        vendor_extensions = register_hook.collect_from_bundle(VendorBundle())
        assert len(vendor_extensions) == 1
        assert 'awesome' in vendor_extensions
        vendor_ext = vendor_extensions['awesome']
        assert vendor_ext == awesome

        app_extensions = register_hook.collect_from_bundle(MyAppBundle())
        assert len(app_extensions) == 1
        assert 'myext' in app_extensions
        vendor_ext = app_extensions['myext']
        assert vendor_ext == (myext, ['awesome'])

    def test_process_objects(self, app, register_hook: RegisterExtensionsHook):
        register_hook.process_objects(app, FAKE_EXTENSIONS)

        registered = list(register_hook.unchained.extensions.keys())
        assert registered == ['one', 'two', 'three', 'four']
        for name, ext in register_hook.unchained.extensions.items():
            assert name == ext.name
            assert ext.app is None

    def test_run_hook(self, app, register_hook: RegisterExtensionsHook):
        register_hook.run_hook(app, [EmptyBundle(), VendorBundle(), MyAppBundle()])

        registered = list(register_hook.unchained.extensions.keys())
        extensions = list(register_hook.unchained.extensions.values())
        assert registered == ['awesome', 'myext']
        assert extensions == [awesome, myext]


class TestInitExtensionsHook:
    def test_process_objects(self, app, init_hook: InitExtensionsHook):
        init_hook.process_objects(app, FAKE_EXTENSIONS)

        registered = list(init_hook.unchained.extensions.keys())
        assert registered == ['four', 'two', 'three', 'one']
        for name, ext in init_hook.unchained.extensions.items():
            assert name == ext.name
            assert ext.app == app

    def test_resolve_extension_order(self, init_hook: InitExtensionsHook):
        order = [ext.name for ext in init_hook.resolve_extension_order(FAKE_EXTENSIONS)]
        assert order == ['four', 'two', 'three', 'one']

    def test_resolve_broken_extension_order(self, init_hook: InitExtensionsHook):
        extensions = {
            'one': (None, ['two']),
            'two': (None, ['one'])
        }
        with pytest.raises(Exception) as e:
            init_hook.resolve_extension_order(extensions)
        assert 'Circular dependency detected' in str(e.value)

    def test_run_hook(self, app, init_hook: InitExtensionsHook):
        init_hook.run_hook(app, [EmptyBundle(), VendorBundle(), MyAppBundle()])

        registered = list(init_hook.unchained.extensions.keys())
        extensions = list(init_hook.unchained.extensions.values())
        assert registered == ['awesome', 'myext']
        assert extensions == [awesome, myext]
        assert awesome.app == app
        assert myext.app == app

    def test_update_shell_context(self, init_hook: InitExtensionsHook):
        ctx = {}
        data = {'one': 1, 'two': 2, 'three': 3}
        init_hook.unchained.extensions = data
        init_hook.update_shell_context(ctx)
        assert ctx == data
