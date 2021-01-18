"""
    flask_unchained
    ---------------

    The quickest and easiest way to build large web apps and APIs with Flask and SQLAlchemy

    :copyright: Copyright © 2018 Brian Cappello
    :license: MIT, see LICENSE for more details
"""

__version__ = '0.8.1'

# must be first
from . import _compat

# aliases
from flask import current_app, g, request, session, _app_ctx_stack, _request_ctx_stack
from flask import render_template, render_template_string
from flask import Request, Response
from flask_wtf.csrf import generate_csrf
from werkzeug.exceptions import abort

from .app_factory import AppFactory
from .app_factory_hook import AppFactoryHook
from .config import BundleConfig
from .bundles import AppBundle, Bundle
from .constants import DEV, PROD, STAGING, TEST
from .di import Service, injectable
from .flask_unchained import FlaskUnchained
from .forms import FlaskForm
from .routes import (controller, resource, func, include, prefix,
                     delete, get, patch, post, put, rule)
from .unchained import Unchained, unchained
from .utils import get_boolean_env
from .views import Controller, Resource
from .views import param_converter, route, no_route, redirect, url_for

# must be last
from .bundles.babel import gettext, ngettext, lazy_gettext, lazy_ngettext
