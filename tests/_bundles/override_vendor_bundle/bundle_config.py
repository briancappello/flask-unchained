from flask_unchained import AppConfig


class BaseConfig(AppConfig):
    VENDOR_KEY1 = 'override_vendor_key1'
    VENDOR_KEY2 = 'override_vendor_key2'


class DevConfig(BaseConfig):
    pass
