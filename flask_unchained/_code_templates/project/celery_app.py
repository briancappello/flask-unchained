import os

from flask_unchained import AppFactory, PROD

# import the celery extension so that celery can access it for its startup
from flask_unchained.bundles.celery import celery


app = AppFactory().create_app(os.getenv('FLASK_ENV', PROD))
app.app_context().push()
