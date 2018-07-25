import os

TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), 'templates')

BUNDLES = [
    'flask_unchained.bundles.babel',
    'flask_unchained.bundles.controller',
    'flask_unchained.bundles.sqlalchemy',
]
