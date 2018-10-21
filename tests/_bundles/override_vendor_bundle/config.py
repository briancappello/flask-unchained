from flask_unchained import AppBundleConfig


class Config(AppBundleConfig):
    VENDOR_KEY1 = 'override_vendor_key1'
    VENDOR_KEY2 = 'override_vendor_key2'
