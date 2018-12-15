import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


def folder_or_none(folder_name):
    if not os.path.exists(os.path.join(PROJECT_ROOT, folder_name)):
        return None
    return folder_name


# these get passed to the FlaskUnchained constructor
TEMPLATE_FOLDER = folder_or_none('templates')
STATIC_FOLDER = folder_or_none('static')
STATIC_URL_PATH = '/static' if STATIC_FOLDER else None


BUNDLES = [
    #! if api:
    'flask_unchained.bundles.api',
    #! endif
    #! if mail:
    'flask_unchained.bundles.mail',
    #! endif
    #! if celery:
    'flask_unchained.bundles.celery',  # move before mail to send emails synchronously
    #! endif
    #! if oauth:
    'flask_unchained.bundles.oauth',
    #! endif
    #! if security or oauth:
    'flask_unchained.bundles.security',
    #! endif
    #! if security or session:
    'flask_unchained.bundles.session',
    #! endif
    #! if security or sqlalchemy:
    'flask_unchained.bundles.sqlalchemy',
    #! endif
    #! if webpack:
    'flask_unchained.bundles.webpack',
    #! endif
    #! if any(set(requirements) - {'dev', 'docs'}):

    #! endif
    'app',  # your app bundle *must* be last
]
