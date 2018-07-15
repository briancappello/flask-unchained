from flask import Blueprint

from flask_unchained.bundles.controller import route


three = Blueprint('three', __name__)
four = Blueprint('four', __name__, url_prefix='/four')


@route(blueprint=three)
def view_three():
    return 'view_three rendered'


@route(blueprint=four)
def view_four():
    return 'view_four rendered'
