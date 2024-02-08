import pytest

from flask_unchained.app_factory import AppFactory, BundleNotFoundError
from flask_unchained.bundles.controller import ControllerBundle

from ._bundles.app_bundle_in_module.bundle import AppBundleInModule
from ._bundles.bundle_in_module.bundle import ModuleBundle
from ._bundles.empty_bundle import EmptyBundle
from ._bundles.myapp import MyAppBundle
from ._bundles.override_vendor_bundle import VendorBundle
from ._bundles.vendor_bundle import VendorBundle as BaseVendorBundle


app_bundle_in_module = "tests._bundles.app_bundle_in_module"
bundle_in_module = "tests._bundles.bundle_in_module"
empty_bundle = "tests._bundles.empty_bundle"
error_bundle = "tests._bundles.error_bundle"
myapp = "tests._bundles.myapp"
override_vendor_bundle = "tests._bundles.override_vendor_bundle"
vendor_bundle = "tests._bundles.vendor_bundle"


class TestLoadBundles:
    def test_bundle_in_module(self):
        app_bundle, bundles = AppFactory().load_bundles([bundle_in_module])
        assert app_bundle is None
        assert len(bundles) == 2
        assert isinstance(bundles[-1], ModuleBundle)

    def test_bundle_in_init(self):
        app_bundle, bundles = AppFactory().load_bundles([empty_bundle])
        assert app_bundle is None
        assert len(bundles) == 2
        assert isinstance(bundles[-1], EmptyBundle)

    def test_no_bundle_found(self):
        with pytest.raises(BundleNotFoundError) as e:
            AppFactory().load_bundles([error_bundle])
        msg = f"Unable to find a Bundle subclass in the {error_bundle} bundle!"
        assert msg in str(e.value)

    def test_multiple_bundles(self):
        app_bundle, bundles = AppFactory().load_bundles(
            [bundle_in_module, empty_bundle, vendor_bundle]
        )
        assert app_bundle is None
        assert isinstance(bundles[-1], BaseVendorBundle)
        assert set(bundles) == {
            ControllerBundle(),
            ModuleBundle(),
            EmptyBundle(),
            BaseVendorBundle(),
        }

    def test_multiple_bundles_including_app_bundle(self):
        app_bundle, bundles = AppFactory().load_bundles(
            [bundle_in_module, empty_bundle, override_vendor_bundle, myapp]
        )
        assert isinstance(app_bundle, MyAppBundle)
        assert isinstance(bundles[-1], MyAppBundle)
        assert set(bundles) == {
            ControllerBundle(),
            ModuleBundle(),
            EmptyBundle(),
            VendorBundle(),
            MyAppBundle(),
        }

    def test_multiple_bundles_including_app_bundle_in_module(self):
        app_bundle, bundles = AppFactory().load_bundles(
            [bundle_in_module, override_vendor_bundle, app_bundle_in_module]
        )
        assert isinstance(app_bundle, AppBundleInModule)
        assert isinstance(bundles[-1], AppBundleInModule)
        assert set(bundles) == {
            ControllerBundle(),
            ModuleBundle(),
            VendorBundle(),
            AppBundleInModule(),
        }
