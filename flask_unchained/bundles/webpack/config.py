import os

from flask_unchained import AppConfig


class Config(AppConfig):
    WEBPACK_MANIFEST_PATH = os.path.join(
        AppConfig.STATIC_FOLDER, 'assets', 'manifest.json')


class ProdConfig:
    # use relative paths by default, ie, the same host as the backend
    WEBPACK_ASSETS_HOST = ''


class StagingConfig(ProdConfig):
    pass
