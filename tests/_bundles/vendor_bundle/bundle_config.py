from flask_unchained import AppConfig


class BaseConfig(AppConfig):
    VENDOR_KEY1 = 'vendor_key1'
    VENDOR_KEY2 = 'vendor_key2'


class DevConfig(BaseConfig):
    pass
