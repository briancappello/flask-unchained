from flask_babelex import Domain
from werkzeug import ImmutableDict


class Config:
    LANGUAGES = ['en']
    DEFAULT_LOCALE = 'en'
    DEFAULT_TIMEZONE = 'UTC'
    DEFAULT_DOMAIN = Domain()
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


class DevConfig:
    LAZY_TRANSLATIONS = False


class ProdConfig:
    LAZY_TRANSLATIONS = True


class StagingConfig(ProdConfig):
    pass


class TestConfig:
    TESTING = True
