from flask_unchained import (
    controller,
    delete,
    func,
    get,
    include,
    patch,
    post,
    prefix,
    put,
    resource,
    rule,
)

from .views import OAuthController


routes = lambda: [
    controller(OAuthController),
]
