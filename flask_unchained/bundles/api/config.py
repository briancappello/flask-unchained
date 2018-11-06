from flask_unchained import BundleConfig


class Config(BundleConfig):
    """
    Default config settings for the API Bundle.
    """

    API_OPENAPI_VERSION = '2.0'
    API_REDOC_SOURCE_URL = \
        'https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js'

    API_REDOC_URL_PREFIX = '/api-docs'
    API_REDOC_PATH = '/'
    API_OPENAPI_JSON_PATH = 'openapi.json'

    API_TITLE = None
    API_VERSION = 1
    API_DESCRIPTION = None

    API_APISPEC_PLUGINS = None
