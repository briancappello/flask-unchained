from flask_login.utils import _get_user
from werkzeug.local import LocalProxy

current_user = LocalProxy(_get_user)
