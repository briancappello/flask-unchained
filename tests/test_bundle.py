import os

from flask_unchained import Bundle

from ._bundles.myapp import MyAppBundle
from ._bundles.empty_bundle import EmptyBundle
from ._bundles.vendor_bundle import VendorBundle
from ._bundles.override_vendor_bundle import VendorBundle as OverrideVendorBundle


class FoobarBundle(Bundle):
    name = 'foobaz'


class TestBundleDescriptors:
    def test_module_name_descriptor_works_automatically(self):
        assert FoobarBundle.module_name == 'tests.test_bundle'

    def test_it_strips_bundle_module_suffix_from_declared_module_name(self):
        class FooBundle(Bundle):
            module_name = 'tests.foo.bundle'
        assert FooBundle.module_name == 'tests.foo'

    def test_module_name_descriptor_strips_bundle_module_suffix(self):
        assert VendorBundle.module_name == 'tests._bundles.vendor_bundle'

    def test_declared_name_descriptor(self):
        assert FoobarBundle.name == 'foobaz'

    def test_automatic_name_descriptor(self):
        class AmazingBundle(Bundle):
            pass
        assert AmazingBundle.name == 'amazing_bundle'

    def test_automatic_app_bundle_name_descriptor(self):
        assert MyAppBundle.name == 'my_app'

    def test_folder_descriptor(self):
        cwd = os.getcwd()
        assert MyAppBundle.folder == cwd + '/tests/_bundles/myapp'
        assert VendorBundle.folder == cwd + '/tests/_bundles/vendor_bundle'

    def test_static_folder_descriptor(self):
        cwd = os.getcwd()
        assert MyAppBundle().static_folder == \
               cwd + '/tests/_bundles/myapp/static'
        assert VendorBundle().static_folder == \
               cwd + '/tests/_bundles/vendor_bundle/static'
        assert EmptyBundle().static_folder is None

    def test_static_url_path_descriptor(self):
        assert MyAppBundle().static_url_path == '/my-app/static'
        assert VendorBundle().static_url_path is None
        assert EmptyBundle().static_url_path is None

    def test_template_folder_descriptor(self):
        cwd = os.getcwd()
        assert MyAppBundle().template_folder == \
               cwd + '/tests/_bundles/myapp/templates'
        assert VendorBundle().template_folder == \
               cwd + '/tests/_bundles/vendor_bundle/templates'
        assert EmptyBundle().template_folder is None


class TestBundleDescriptorsWithInheritance:
    def test_module_name(self):
        assert OverrideVendorBundle.module_name == 'tests._bundles.override_vendor_bundle'

    def test_folder(self):
        cwd = os.getcwd()
        assert OverrideVendorBundle.folder == \
               cwd + '/tests/_bundles/override_vendor_bundle'

    def test_name(self):
        assert OverrideVendorBundle.name == 'vendor_bundle'

    def test_static_folder(self):
        assert OverrideVendorBundle().static_folder is None

    def test_static_url_path(self):
        assert OverrideVendorBundle().static_url_path == '/vendor-bundle/static'

    def test_template_folder(self):
        assert OverrideVendorBundle().template_folder is None


class TestBundle:
    def test_repr(self):
        expected = "<FoobarBundle name='foobaz' module='tests.test_bundle'>"
        assert str(FoobarBundle) == expected

    def test_iter_class_hierarchy(self):
        hierarchy = list(OverrideVendorBundle().iter_class_hierarchy())
        assert len(hierarchy) == 2
        assert isinstance(hierarchy[0], VendorBundle)
        assert isinstance(hierarchy[1], OverrideVendorBundle)

        hierarchy = list(OverrideVendorBundle().iter_class_hierarchy(include_self=False))
        assert len(hierarchy) == 1
        assert isinstance(hierarchy[0], VendorBundle)

        hierarchy = list(OverrideVendorBundle().iter_class_hierarchy(reverse=False))
        assert len(hierarchy) == 2
        assert isinstance(hierarchy[0], OverrideVendorBundle)
        assert isinstance(hierarchy[1], VendorBundle)

    def test_has_views(self):
        assert MyAppBundle().has_views() is False
        assert VendorBundle().has_views() is True
        assert OverrideVendorBundle().has_views() is True

    def test_blueprint_name(self):
        assert MyAppBundle().blueprint_name == 'my_app'
        assert VendorBundle().blueprint_name == 'vendor_bundle_0'
        assert OverrideVendorBundle().blueprint_name == 'vendor_bundle'

    def test_static_folders(self):
        assert MyAppBundle().static_folders == [MyAppBundle().static_folder]
        assert VendorBundle().static_folders == []
        assert OverrideVendorBundle().static_folders == [VendorBundle().static_folder]
