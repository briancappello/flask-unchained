from flask_unchained import AppConfig


class Config(AppConfig):
    SECRET_KEY = 'change-me'
    APP_KEY = 'app_key'
    VENDOR_KEY1 = 'app_override'
