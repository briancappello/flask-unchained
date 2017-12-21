import pytest

from flask_unchained import unchained, AppConfig
from flask_unchained.hooks.register_extensions_hook import (
    ExtensionTuple, RegisterExtensionsHook)

from .fixtures.app_bundle import AppBundle, myext
from .fixtures.app_bundle.extensions import MyExtension

from .fixtures.empty_bundle import EmptyBundle

from .fixtures.vendor_bundle import VendorBundle, awesome
from .fixtures.vendor_bundle.extension import AwesomeExtension


hook = RegisterExtensionsHook()


class TestRegisterExtensionsHook:
    def test_type_check(self):
        assert hook.type_check(AwesomeExtension) is False
        assert hook.type_check(awesome) is True

        assert hook.type_check(MyExtension) is False
        assert hook.type_check(myext) is True

    def test_collect_from_bundle(self):
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

    def test_resolve_extension_order(self):
        exts = [
            ExtensionTuple('four', None, []),
            ExtensionTuple('three', None, ['four']),
            ExtensionTuple('two', None, ['four']),
            ExtensionTuple('one', None, ['two', 'three'])
        ]
        order = hook.resolve_extension_order(exts)
        assert order == ['four', 'three', 'two', 'one']

    def test_resolve_broken_extension_order(self):
        exts = [
            ExtensionTuple('one', None, ['two']),
            ExtensionTuple('two', None, ['one']),
        ]
        with pytest.raises(Exception) as e:
            hook.resolve_extension_order(exts)
        assert 'Circular dependency detected' in str(e)

    def test_process_objects(self, app):
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
        hook.process_objects(app, AppConfig, exts)

        registered = list(unchained._extensions.keys())
        assert registered == ['four', 'three', 'two', 'one']
        for name, ext in unchained._extensions.items():
            assert name == ext.name
            assert ext.app == app

    def test_run_hook(self, app):
        hook.run_hook(app, AppConfig, [EmptyBundle, VendorBundle, AppBundle])

        registered = list(unchained._extensions.keys())
        exts = list(unchained._extensions.values())
        assert registered == ['awesome', 'myext']
        assert exts == [awesome, myext]
        assert awesome.app == app
        assert myext.app == app

    def test_update_shell_context(self, app):
        ctx = {}
        expected = {'one': 1, 'two': 2, 'three': 3}
        unchained._extensions = expected
        hook.update_shell_context(app, ctx)
        assert ctx == expected
