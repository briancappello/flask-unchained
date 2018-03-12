from flask_unchained import AppConfig as BaseConfig


class TestConfig(BaseConfig):
    TESTING = True
