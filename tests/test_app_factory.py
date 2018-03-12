import pytest

from flask_unchained import app_factory

from ._bundles.app_bundle_in_module.bundle import AppBundleInModule
from ._bundles.bundle_in_module.bundle import ModuleBundle
from ._bundles.empty_bundle import EmptyBundle
from ._bundles.myapp import MyAppBundle
from ._bundles.override_vendor_bundle import VendorBundle
from ._bundles.vendor_bundle import VendorBundle as BaseVendorBundle

app_bundle_in_module = 'tests._bundles.app_bundle_in_module'
bundle_in_module = 'tests._bundles.bundle_in_module'
empty_bundle = 'tests._bundles.empty_bundle'
error_bundle = 'tests._bundles.error_bundle'
myapp = 'tests._bundles.myapp'
override_vendor_bundle = 'tests._bundles.override_vendor_bundle'
vendor_bundle = 'tests._bundles.vendor_bundle'


class TestLoadBundles:
    def test_bundle_in_module(self):
        results = app_factory._load_bundles([bundle_in_module])
        assert results == [ModuleBundle]

    def test_bundle_in_init(self):
        results = app_factory._load_bundles([empty_bundle])
        assert results == [EmptyBundle]

    def test_no_bundle_found(self):
        with pytest.raises(app_factory.BundleNotFoundError) as e:
            app_factory._load_bundles([error_bundle])
        msg = f'Unable to find a Bundle subclass in the {error_bundle} bundle!'
        assert msg in str(e)

    def test_multiple_bundles(self):
        results = app_factory._load_bundles([bundle_in_module,
                                             empty_bundle,
                                             vendor_bundle])
        assert results == [ModuleBundle, EmptyBundle, BaseVendorBundle]

    def test_multiple_bundles_including_app_bundle(self):
        results = app_factory._load_bundles([bundle_in_module,
                                             empty_bundle,
                                             override_vendor_bundle,
                                             myapp])
        assert results == [ModuleBundle, EmptyBundle, VendorBundle, MyAppBundle]

    def test_load_app_bundle(self):
        result = app_factory._load_app_bundle(myapp)
        assert result == MyAppBundle

    def test_load_app_bundle_in_module(self):
        result = app_factory._load_app_bundle(app_bundle_in_module)
        assert result == AppBundleInModule

    def test_load_app_bundle_on_non_app_bundle(self):
        with pytest.raises(app_factory.BundleNotFoundError):
            app_factory._load_app_bundle(vendor_bundle)

    def test_load_app_bundle_on_empty_package(self):
        with pytest.raises(app_factory.BundleNotFoundError):
            app_factory._load_app_bundle(empty_bundle)
