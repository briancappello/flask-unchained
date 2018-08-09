"""
Controller Bundle
-----------------

Adds class-based views and declarative routing to Flask Unchained.

Installation
~~~~~~~~~~~~

The controller bundle is always used, even if not specified in your
``unchained_config.py``. But it doesn't hurt to list it if you want::

    # file: your_project_root/unchained_config.py
    BUNDLES = [
        'flask_unchained.bundles.controller',
        # ...
    ]

.. autoclass:: ControllerBundle
    :members:
    :exclude-members: method_as_view

.. automodule:: flask_unchained.bundles.controller.controller
    :members:

.. automodule:: flask_unchained.bundles.controller.decorators
    :members:

.. automodule:: flask_unchained.bundles.controller.resource
    :members:

.. automodule:: flask_unchained.bundles.controller.routes
    :members:

.. automodule:: flask_unchained.bundles.controller.utils
    :members:
"""

from collections import defaultdict
from flask_unchained import Bundle, FlaskUnchained
from flask_unchained.utils import AttrDict

from .constants import (ALL_METHODS, INDEX_METHODS, MEMBER_METHODS,
                        CREATE, DELETE, GET, LIST, PATCH, PUT)
from .controller import Controller
from .decorators import no_route, route
from .resource import Resource
from .routes import (
    controller, func, get, include, patch, post, prefix, put, resource, rule)
from .utils import redirect, url_for


class ControllerBundle(Bundle):
    """
    The :class:`Bundle` subclass for the controller bundle.
    """

    def __init__(self):
        self.store = AttrDict(
            # endpoint name -> Route
            endpoints={},

            # f'{ControllerClassName}.{view_method_name}' -> Route
            controller_endpoints={},

            # bundle name -> List[Route]
            bundle_routes=defaultdict(list),

            # List[Route]
            other_routes=[],
        )

    def before_init_app(self, app: FlaskUnchained):
        """
        Configure the Jinja environment and template loader.
        """
        from .templates import (UnchainedJinjaEnvironment,
                                UnchainedJinjaLoader)
        app.jinja_environment = UnchainedJinjaEnvironment
        app.jinja_options = {**app.jinja_options,
                             'loader': UnchainedJinjaLoader(app)}
        app.jinja_env.globals['url_for'] = url_for

    def after_init_app(self, app: FlaskUnchained):
        """
        Configure an after request hook to set the ``csrf_token`` in the cookie.
        """

        from flask_wtf.csrf import generate_csrf

        # send CSRF token in the cookie
        @app.after_request
        def set_csrf_cookie(response):
            if response:
                response.set_cookie('csrf_token', generate_csrf())
            return response
