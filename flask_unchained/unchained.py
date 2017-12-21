from flask import current_app
from werkzeug.local import LocalProxy


unchained = LocalProxy(lambda: current_app.extensions['unchained'])
