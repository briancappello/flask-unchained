from flask_unchained import Bundle

from ._bundles.myapp import MyAppBundle
from ._bundles.vendor_bundle import VendorBundle


class FoobarBundle(Bundle):
    name = 'foobaz'


class TestBundle:
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

    def test_repr(self):
        expected = "<FoobarBundle name='foobaz' module='tests.test_bundle'>"
        assert str(FoobarBundle) == expected
