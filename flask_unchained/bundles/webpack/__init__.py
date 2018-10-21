from flask_unchained import Bundle

from .extensions import Webpack, webpack


class WebpackBundle(Bundle):
    """
    The :class:`~flask_unchained.Bundle` subclass for the webpack bundle. Has no special
    behavior.
    """
    pass
