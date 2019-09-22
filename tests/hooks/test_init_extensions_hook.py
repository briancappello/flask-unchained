import pytest

from flask_unchained.hooks.init_extensions_hook import InitExtensionsHook
from flask_unchained.hooks.register_extensions_hook import ExtensionTuple
from flask_unchained.unchained import Unchained

from .._bundles.myapp import MyAppBundle, myext
from .._bundles.empty_bundle import EmptyBundle
from .._bundles.vendor_bundle import VendorBundle, awesome


@pytest.fixture
def hook():
    return InitExtensionsHook(Unchained())


class TestRegisterExtensionsHook:
    def test_collect_from_bundle(self, hook: InitExtensionsHook):
        assert hook.collect_from_bundle(EmptyBundle()) == {}

        vendor_extensions = hook.collect_from_bundle(VendorBundle())
        assert len(vendor_extensions) == 1
        assert 'awesome' in vendor_extensions
        vendor_ext = vendor_extensions['awesome']
        assert vendor_ext == awesome

        app_extensions = hook.collect_from_bundle(MyAppBundle())
        assert len(app_extensions) == 1
        assert 'myext' in app_extensions
        vendor_ext = app_extensions['myext']
        assert vendor_ext == (myext, ['awesome'])

    def test_resolve_extension_order(self, hook: InitExtensionsHook):
        extensions = {
            'one': (None, ['two', 'three']),
            'two': (None, ['four']),
            'three': (None, ['four']),
            'four': None,
        }
        order = [ext.name for ext in hook.resolve_extension_order(extensions)]
        assert order == ['four', 'two', 'three', 'one']

    def test_resolve_broken_extension_order(self, hook: InitExtensionsHook):
        extensions = {
            'one': (None, ['two']),
            'two': (None, ['one'])
        }
        with pytest.raises(Exception) as e:
            hook.resolve_extension_order(extensions)
        assert 'Circular dependency detected' in str(e.value)

    def test_process_objects(self, app, hook: InitExtensionsHook):
        class FakeExt:
            def __init__(self, name):
                self.app = None
                self.name = name

            def init_app(self, app):
                self.app = app

        extensions = {
            'one': (FakeExt('one'), ['two', 'three']),
            'two': (FakeExt('two'), ['four']),
            'three': (FakeExt('three'), ['four']),
            'four': FakeExt('four'),
        }
        hook.process_objects(app, extensions)

        registered = list(hook.unchained.extensions.keys())
        assert registered == ['four', 'two', 'three', 'one']
        for name, ext in hook.unchained.extensions.items():
            assert name == ext.name
            assert ext.app == app

    def test_run_hook(self, app, hook: InitExtensionsHook):
        hook.run_hook(app, [EmptyBundle(), VendorBundle(), MyAppBundle()])

        registered = list(hook.unchained.extensions.keys())
        extensions = list(hook.unchained.extensions.values())
        assert registered == ['awesome', 'myext']
        assert extensions == [awesome, myext]
        assert awesome.app == app
        assert myext.app == app

    def test_update_shell_context(self, hook: InitExtensionsHook):
        ctx = {}
        data = {'one': 1, 'two': 2, 'three': 3}
        hook.unchained.extensions = data
        hook.update_shell_context(ctx)
        assert ctx == data
