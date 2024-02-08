"""
    flask_unchained
    ---------------

    The quickest and easiest way to build large web apps and APIs with Flask and SQLAlchemy

    :copyright: Copyright © 2018 Brian Cappello
    :license: MIT, see LICENSE for more details
"""

__version__ = "0.9.0"

# must be first
from . import _compat  # isort: skip

# aliases
from flask import (
    Request,
    Response,
    current_app,
    g,
    render_template,
    render_template_string,
    request,
    session,
)
from werkzeug.exceptions import abort

from .app_factory import AppFactory
from .app_factory_hook import AppFactoryHook
from .bundles import AppBundle, Bundle
from .config import BundleConfig
from .constants import DEV, PROD, STAGING, TEST
from .di import Service, injectable
from .flask_unchained import FlaskUnchained
from .forms import FlaskForm
from .routes import (
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
from .unchained import Unchained, unchained
from .utils import get_boolean_env


# must be last
from .bundles.babel import gettext, lazy_gettext, lazy_ngettext, ngettext  # isort: skip
from .views import (  # isort: skip
    Controller,
    Resource,
    no_route,
    param_converter,
    redirect,
    route,
    url_for,
)
