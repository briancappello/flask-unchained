from flask import jsonify
from flask_unchained import BundleConfig
from flask_unchained.string_utils import camel_case, snake_case


class Config(BundleConfig):
    """
    Default config settings for the API Bundle.
    """

    API_OPENAPI_VERSION = '3.0.2'
    API_REDOC_SOURCE_URL = \
        'https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js'

    API_TITLE = None
    API_VERSION = 1
    API_DESCRIPTION = None

    API_APISPEC_PLUGINS = None

    DUMP_KEY_FN = camel_case
    """
    An optional function to use for converting keys when dumping data to send over
    the wire. By default, we convert snake_case to camelCase.
    """

    LOAD_KEY_FN = snake_case
    """
    An optional function to use for converting keys received over the wire to
    the backend's representation. By default, we convert camelCase to snake_case.
    """

    ACCEPT_HANDLERS = {'application/json': jsonify}
    """
    Functions to use for converting response data for Accept headers.
    """
