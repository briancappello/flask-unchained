import os

from flask_unchained import BundleConfig


class Config(BundleConfig):
    WEBPACK_MANIFEST_PATH = (
        None if not BundleConfig.current_app.static_folder
        else os.path.join(BundleConfig.current_app.static_folder,
                          'assets', 'manifest.json'))


class ProdConfig(Config):
    # use relative paths by default, ie, the same host as the backend
    WEBPACK_ASSETS_HOST = ''


class StagingConfig(ProdConfig):
    pass
