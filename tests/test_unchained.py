import pytest

from flask_unchained.unchained import Unchained

from .fixtures.myapp import AppBundle
from .fixtures.myapp.config import DevConfig
from .fixtures.vendor_bundle import VendorBundle, awesome
from .fixtures.vendor_bundle.hooks import Store as VendorBundleStore


def test_unchained(app):
    unchained = Unchained()
    unchained.init_app(app, DevConfig, [VendorBundle, AppBundle])
    assert 'unchained' in app.extensions
    assert app.extensions['unchained'] == unchained

    with pytest.raises(AttributeError):
        fail = unchained.app

    assert isinstance(unchained.vendor_bundle, VendorBundleStore)
    assert unchained.ext.awesome == awesome
