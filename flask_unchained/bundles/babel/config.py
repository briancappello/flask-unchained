from flask_babelex import Domain
from flask_unchained import BundleConfig
from werkzeug import ImmutableDict


class Config(BundleConfig):
    """
    Default configuration options for the Babel Bundle.
    """

    LANGUAGES = ['en']
    """
    The language codes supported by the app.
    """

    BABEL_DEFAULT_LOCALE = 'en'
    """
    The default language to use if none is specified by the client's browser.
    """

    BABEL_DEFAULT_TIMEZONE = 'UTC'
    """
    The default timezone to use.
    """

    DEFAULT_DOMAIN = Domain()
    """
    The default :class:`~flask_babelex.Domain` to use.
    """

    DATE_FORMATS = ImmutableDict({
        'time':             'medium',
        'date':             'medium',
        'datetime':         'medium',
        'time.short':       None,
        'time.medium':      None,
        'time.full':        None,
        'time.long':        None,
        'date.short':       None,
        'date.medium':      None,
        'date.full':        None,
        'date.long':        None,
        'datetime.short':   None,
        'datetime.medium':  None,
        'datetime.full':    None,
        'datetime.long':    None,
    })
    """
    A dictionary of date formats.
    """

    ENABLE_URL_LANG_CODE_PREFIX = False
    """
    Whether or not to enable the capability to specify the language code as part of
    the URL.
    """


class DevConfig(Config):
    LAZY_TRANSLATIONS = False


class ProdConfig(Config):
    LAZY_TRANSLATIONS = True


class StagingConfig(ProdConfig):
    pass
