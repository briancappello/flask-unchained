from flask_unchained import Bundle

from .extensions import Webpack, webpack


class WebpackBundle(Bundle):
    """
    The Webpack Bundle.
    """

    name = 'webpack_bundle'
    """
    The name of the Webpack Bundle.
    """
