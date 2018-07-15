from flask import Blueprint

from flask_unchained.bundles.controller import route


not_loaded = Blueprint('not_loaded', __name__)


@route(only_if=False)
def silly_condition():
    return 'silly_condition'
