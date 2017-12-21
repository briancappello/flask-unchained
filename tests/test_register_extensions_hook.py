import pytest

from flask_unchained.hooks.register_extensions_hook import (
    ExtensionTuple, RegisterExtensionsHook)
from flask_unchained.unchained_extension import UnchainedStore

from .fixtures.myapp import AppBundle, myext
from .fixtures.myapp.extensions import MyExtension

from .fixtures.empty_bundle import EmptyBundle

from .fixtures.vendor_bundle import VendorBundle, awesome
from .fixtures.vendor_bundle.extension import AwesomeExtension


@pytest.fixture
def hook():
    return RegisterExtensionsHook(UnchainedStore(None))


class TestRegisterExtensionsHook:
    def test_type_check(self, hook):
        assert hook.type_check(AwesomeExtension) is False
        assert hook.type_check(awesome) is True

        assert hook.type_check(MyExtension) is False
        assert hook.type_check(myext) is True

    def test_collect_from_bundle(self, hook):
        assert hook.collect_from_bundle(EmptyBundle) == []

        vendor_extensions = hook.collect_from_bundle(VendorBundle)
        assert len(vendor_extensions) == 1
        vendor_ext = vendor_extensions[0]
        assert vendor_ext.name == 'awesome'
        assert vendor_ext.extension == awesome
        assert vendor_ext.dependencies == []

        app_extensions = hook.collect_from_bundle(AppBundle)
        assert len(app_extensions) == 1
        vendor_ext = app_extensions[0]
        assert vendor_ext.name == 'myext'
        assert vendor_ext.extension == myext
        assert vendor_ext.dependencies == ['awesome']

    def test_resolve_extension_order(self, hook):
        exts = [
            ExtensionTuple('four', None, []),
            ExtensionTuple('three', None, ['four']),
            ExtensionTuple('two', None, ['four']),
            ExtensionTuple('one', None, ['two', 'three'])
        ]
        order = [ext.name for ext in hook.resolve_extension_order(exts)]
        assert order == ['four', 'three', 'two', 'one']

    def test_resolve_broken_extension_order(self, hook):
        exts = [
            ExtensionTuple('one', None, ['two']),
            ExtensionTuple('two', None, ['one']),
        ]
        with pytest.raises(Exception) as e:
            hook.resolve_extension_order(exts)
        assert 'Circular dependency detected' in str(e)

    def test_process_objects(self, app, hook):
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

        registered = list(hook.unchained._extensions.keys())
        assert registered == ['four', 'three', 'two', 'one']
        for name, ext in hook.unchained._extensions.items():
            assert name == ext.name
            assert ext.app == app

    def test_run_hook(self, app, hook):
        hook.run_hook(app, [EmptyBundle, VendorBundle, AppBundle])

        registered = list(hook.unchained._extensions.keys())
        exts = list(hook.unchained._extensions.values())
        assert registered == ['awesome', 'myext']
        assert exts == [awesome, myext]
        assert awesome.app == app
        assert myext.app == app

    def test_update_shell_context(self, hook):
        ctx = {}
        data = {'one': 1, 'two': 2, 'three': 3}
        hook.unchained._extensions = data
        hook.update_shell_context(ctx)
        data['unchained'] = hook.unchained
        assert ctx == data
