import pytest

from flask_unchained import unchained as exported_unchained
from flask_unchained.unchained_extension import UnchainedExtension

from .fixtures.myapp import AppBundle
from .fixtures.myapp.config import DevConfig
from .fixtures.vendor_bundle import VendorBundle, awesome
from .fixtures.vendor_bundle.vendor_bundle_store import VendorBundleStore


def test_unchained(app):
    unchained_ext = UnchainedExtension()
    unchained = unchained_ext.init_app(app, DevConfig, [VendorBundle, AppBundle])
    assert 'unchained' in app.extensions
    assert app.extensions['unchained'] == unchained == exported_unchained

    with pytest.raises(AttributeError):
        fail = unchained.app

    assert isinstance(unchained.vendor_bundle, VendorBundleStore)
    assert unchained.ext.awesome == awesome
