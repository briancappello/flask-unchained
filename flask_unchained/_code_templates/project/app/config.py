import os

from flask_unchained import AppBundleConfig, get_boolean_env


class Config(AppBundleConfig):
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'change-me-to-a-secret-key!')
#! if security or session:
    #! SESSION_TYPE = "{{ 'sqlalchemy' if sqlalchemy else 'filesystem' }}"
#! endif
#! if mail:

    MAIL_DEFAULT_SENDER = f"noreply@localhost"  # FIXME
#! endif
#! if webpack:

    WEBPACK_MANIFEST_PATH = os.path.join('static', 'assets', 'manifest.json')
#! endif


class DevConfig(Config):
    EXPLAIN_TEMPLATE_LOADING = False
#! if security or sqlalchemy:
    SQLALCHEMY_ECHO = False
#! endif
#! if webpack:

    WEBPACK_ASSETS_HOST = 'http://localhost:3333'
#! endif


class ProdConfig(Config):
    pass


class StagingConfig(ProdConfig):
    pass


class TestConfig(Config):
    TESTING = True
