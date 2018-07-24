"""
    flask_unchained.bundles.webpack
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Adds Webpack support to Flask Unchained

    :copyright: Copyright © 2018 Brian Cappello
    :license: MIT, see LICENSE for more details
"""


__version__ = '0.2.0'


from flask_unchained import Bundle

from .extensions import webpack


class WebpackBundle(Bundle):
    pass
