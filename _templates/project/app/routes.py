from flask_unchained import (controller, resource, func, include, prefix,
                             get, post, patch, put, rule)

from .views import SiteController


routes = lambda: [
    controller(SiteController),
]
