from flask_unchained import Bundle

from .extensions import myext


class AppBundle(Bundle):
    app_bundle = True
