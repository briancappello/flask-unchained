import pytest

from flask_unchained.unchained import Unchained

from ._bundles.myapp import MyAppBundle
from ._bundles.myapp.config import DevConfig
from ._bundles.vendor_bundle import VendorBundle, awesome
from ._bundles.vendor_bundle.hooks import Store as VendorBundleStore


def test_unchained(app):
    unchained = Unchained()
    unchained.init_app(app, DevConfig, [VendorBundle, MyAppBundle])
    assert 'unchained' in app.extensions
    assert app.extensions['unchained'] == unchained

    with pytest.raises(AttributeError):
        fail = unchained.app

    assert isinstance(unchained.vendor_bundle, VendorBundleStore)
    assert unchained.extensions.awesome == awesome
