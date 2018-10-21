from flask_unchained import AppBundleConfig


class Config(AppBundleConfig):
    SECRET_KEY = 'change-me'
    APP_KEY = 'app_key'
    VENDOR_KEY1 = 'app_override'
