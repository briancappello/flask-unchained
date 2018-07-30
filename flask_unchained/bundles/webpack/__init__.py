"""
    Webpack Bundle
    --------------

    Adds Webpack support to Flask Unchained
"""

from flask_unchained import Bundle

from .extensions import webpack


class WebpackBundle(Bundle):
    pass
