from flask_unchained import BundleConfig


class Config(BundleConfig):
    # Default values; override as necessary
    CORS_ORIGINS = '*'
    CORS_METHODS = ALL_METHODS
    CORS_ALLOW_HEADERS = '*'
    CORS_EXPOSE_HEADERS = None
    CORS_SUPPORTS_CREDENTIALS = False
    CORS_MAX_AGE = None
    CORS_SEND_WILDCARD = False
    CORS_AUTOMATIC_OPTIONS = True
    CORS_VARY_HEADER = True
    CORS_RESOURCES = r'/*'
    CORS_INTERCEPT_EXCEPTIONS = True
    CORS_ALWAYS_SEND = True
