import pytest

from flask_unchained.hooks.init_extensions_hook import (
    ExtensionTuple, InitExtensionsHook)
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

        vendor_extensions = hook.get_extension_tuples(
            hook.collect_from_bundle(VendorBundle()))
        assert len(vendor_extensions) == 1
        vendor_ext = vendor_extensions[0]
        assert vendor_ext.name == 'awesome'
        assert vendor_ext.extension == awesome
        assert vendor_ext.dependencies == []

        app_extensions = hook.get_extension_tuples(
            hook.collect_from_bundle(MyAppBundle()))
        assert len(app_extensions) == 1
        vendor_ext = app_extensions[0]
        assert vendor_ext.name == 'myext'
        assert vendor_ext.extension == myext
        assert vendor_ext.dependencies == ['awesome']

    def test_resolve_extension_order(self, hook: InitExtensionsHook):
        exts = [
            ExtensionTuple('four', None, []),
            ExtensionTuple('three', None, ['four']),
            ExtensionTuple('two', None, ['four']),
            ExtensionTuple('one', None, ['two', 'three'])
        ]
        order = [ext.name for ext in hook.resolve_extension_order(exts)]
        assert order == ['four', 'two', 'three', 'one']

    def test_resolve_broken_extension_order(self, hook: InitExtensionsHook):
        exts = [
            ExtensionTuple('one', None, ['two']),
            ExtensionTuple('two', None, ['one']),
        ]
        with pytest.raises(Exception) as e:
            hook.resolve_extension_order(exts)
        assert 'Circular dependency detected' in str(e)

    def test_process_objects(self, app, hook: InitExtensionsHook):
        class FakeExt:
            def __init__(self, name):
                self.app = None
                self.name = name

            def init_app(self, app):
                self.app = app

        exts = [
            ExtensionTuple('four', FakeExt('four'), []),
            ExtensionTuple('three', FakeExt('three'), ['four']),
            ExtensionTuple('two', FakeExt('two'), ['four']),
            ExtensionTuple('one', FakeExt('one'), ['two', 'three'])
        ]
        hook.process_objects(app, exts)

        registered = list(hook.unchained.extensions.keys())
        assert registered == ['four', 'two', 'three', 'one']
        for name, ext in hook.unchained.extensions.items():
            assert name == ext.name
            assert ext.app == app

    def test_run_hook(self, app, hook: InitExtensionsHook):
        hook.run_hook(app, [EmptyBundle(), VendorBundle(), MyAppBundle()])

        registered = list(hook.unchained.extensions.keys())
        exts = list(hook.unchained.extensions.values())
        assert registered == ['awesome', 'myext']
        assert exts == [awesome, myext]
        assert awesome.app == app
        assert myext.app == app

    def test_update_shell_context(self, hook: InitExtensionsHook):
        ctx = {}
        data = {'one': 1, 'two': 2, 'three': 3}
        hook.unchained.extensions = data
        hook.update_shell_context(ctx)
        data['unchained'] = hook.unchained
        assert ctx == data
