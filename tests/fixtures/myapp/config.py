from flask_unchained import AppConfig


class BaseConfig(AppConfig):
    APP_KEY = 'app_key'
    VENDOR_KEY1 = 'app_override'


class DevConfig(BaseConfig):
    pass
