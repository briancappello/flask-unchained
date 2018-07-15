"""
    flask_unchained.bundles.controller
    ~~~~~~~~~~~~~~~~~~~~~~~

    Adds class-based views and declarative routing to Flask Unchained

    :copyright: Copyright © 2018 Brian Cappello
    :license: MIT, see LICENSE for more details
"""

__version__ = '0.2.1'


from flask import Flask
from flask_unchained import Bundle

from .constants import (ALL_METHODS, INDEX_METHODS, MEMBER_METHODS,
                        CREATE, DELETE, GET, LIST, PATCH, PUT)
from .controller import Controller
from .decorators import no_route, route
from .resource import Resource
from .routes import (
    controller, func, get, include, patch, post, prefix, put, resource, rule)
from .utils import redirect, url_for


class ControllerBundle(Bundle):
    @classmethod
    def before_init_app(cls, app: Flask):
        from .template_loader import (UnchainedJinjaEnvironment,
                                      UnchainedJinjaLoader)
        app.jinja_environment = UnchainedJinjaEnvironment
        app.jinja_options = {**app.jinja_options,
                             'loader': UnchainedJinjaLoader(app)}
        app.jinja_env.globals['url_for'] = url_for
