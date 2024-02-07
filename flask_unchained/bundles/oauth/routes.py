from flask_unchained import (controller, resource, func, include, prefix,
                             get, delete, post, patch, put, rule)

from .views import OAuthController


routes = lambda: [
    controller(OAuthController),
]
