import pytest

from flask_unchained import unchained
from flask_unchained.unchained_extension import Unchained

from .fixtures.app_bundle import AppBundle
from .fixtures.vendor_bundle import VendorBundle
from .fixtures.vendor_bundle.vendor_bundle_store import VendorBundleStore


def test_unchained(app):
    unchained_ext = Unchained()
    unchained_ext.init_app(app, [VendorBundle, AppBundle])
    assert 'unchained' in app.extensions
    assert app.extensions['unchained'] == unchained

    with pytest.raises(AttributeError):
        fail = unchained.app_bundle

    assert isinstance(unchained.vendor_bundle, VendorBundleStore)
