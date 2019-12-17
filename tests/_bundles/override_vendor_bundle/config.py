from flask_unchained import BundleConfig


class Config(BundleConfig):
    VENDOR_KEY1 = 'override_vendor_key1'
    VENDOR_KEY2 = 'override_vendor_key2'
