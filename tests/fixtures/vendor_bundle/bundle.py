from flask_unchained import Bundle

from .vendor_bundle_store import VendorBundleStore


class VendorBundle(Bundle):
    extensions_module_name = 'extension'
    store = VendorBundleStore
