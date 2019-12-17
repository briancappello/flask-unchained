from flask_unchained import BundleConfig


class Config(BundleConfig):
    SECRET_KEY = 'not-secret-key'

    SECURITY_SEND_REGISTER_EMAIL = True
    SECURITY_SEND_PASSWORD_CHANGED_EMAIL = True
    SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = True
