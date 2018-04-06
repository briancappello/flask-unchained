from flask_unchained import AppConfig


class Config(AppConfig):
    VENDOR_KEY1 = 'override_vendor_key1'
    VENDOR_KEY2 = 'override_vendor_key2'
