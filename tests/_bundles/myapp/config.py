from flask_unchained import BundleConfig


class Config(BundleConfig):
    SECRET_KEY = 'change-me'
    APP_KEY = 'app_key'
    VENDOR_KEY1 = 'app_override'
