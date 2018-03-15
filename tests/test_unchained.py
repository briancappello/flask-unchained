import pytest

from flask_unchained.constants import DEV
from flask_unchained.unchained import Unchained

from ._bundles.myapp import MyAppBundle
from ._bundles.vendor_bundle import VendorBundle, awesome
from ._bundles.vendor_bundle.hooks import Store as VendorBundleStore


def test_unchained(app):
    unchained = Unchained()
    unchained.init_app(app, DEV, [VendorBundle, MyAppBundle])
    assert 'unchained' in app.extensions
    assert app.extensions['unchained'] == unchained

    with pytest.raises(AttributeError):
        fail = unchained.app

    assert isinstance(unchained.vendor_bundle, VendorBundleStore)
    assert unchained.extensions.awesome == awesome
