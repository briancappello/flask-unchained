from flask_unchained import Bundle

from .fixtures.app_bundle import AppBundle
from .fixtures.vendor_bundle import VendorBundle


class FoobarBundle(Bundle):
    pass


def test_module_name_descriptor_works_automatically():

    assert FoobarBundle.module_name == 'tests.test_bundle'


def test_it_strips_bundle_from_declared_module_name():
    class FooBundle(Bundle):
        module_name = 'tests.foo.bundle'

    assert FooBundle.module_name == 'tests.foo'


def test_module_name_descriptor_strips_bundle_name_automatically():
    assert VendorBundle.module_name == 'tests.fixtures.vendor_bundle'


def test_name_descriptor_works_automatically():
    assert FoobarBundle.name == 'foobar_bundle'


def test_name_descriptor_can_be_declared():
    assert AppBundle.name == 'app'


def test_repr():
    assert str(FoobarBundle) == "class <Bundle name='foobar_bundle' " \
                                              "module='tests.test_bundle'>"
