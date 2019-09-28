"""
    flask_unchained
    ---------------

    The best way to build Flask apps

    :copyright: Copyright © 2018 Brian Cappello
    :license: MIT, see LICENSE for more details
"""

__version__ = '0.7.9'

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
from .config import AppBundleConfig, BundleConfig
from .bundles import AppBundle, Bundle
from .constants import DEV, PROD, STAGING, TEST
from .decorators import param_converter
from .di import BaseService, injectable
from .flask_unchained import FlaskUnchained
from .forms import FlaskForm
from .routes import (controller, resource, func, include, prefix,
                     delete, get, patch, post, put, rule)
from .unchained import Unchained, unchained
from .utils import get_boolean_env
from .views import Controller, Resource, route, no_route, redirect, url_for

# must be last
from .bundles.babel import gettext, ngettext, lazy_gettext, lazy_ngettext
