"""
    flask_babel_bundle
    ~~~~~~~~~~~~~~~~~~

    Adds support for translations to Flask Unchained

    :copyright: Copyright © 2018 Brian Cappello
    :license: MIT, see LICENSE for details
"""

__version__ = '0.1.0'

import pkg_resources
import re

from flask import Flask, Blueprint, current_app, g, request
from flask_babelex import Domain, gettext as _gettext, ngettext as _ngettext
from flask_unchained import Bundle
from speaklater import make_lazy_string
from typing import *
from werkzeug.local import LocalProxy

from .extensions import babel


TRANSLATION_KEY_RE = re.compile(r'^(?P<domain>[a-z_]+)\.[a-z_.]+$')
PLURAL_TRANSLATION_KEY_RE = re.compile(r'^(?P<domain>[a-z_]+)\.[a-z_.]+\.plural$')


class BabelBundle(Bundle):
    command_group_names = ('babel',)
    enable_url_lang_code_prefix = True
    language_code_key = 'lang_code'

    @classmethod
    def get_url_rule(cls, rule: Optional[str]):
        if not rule:
            return f'/<{cls.language_code_key}>'
        return f'/<{cls.language_code_key}>' + rule

    @classmethod
    def register_blueprint(cls, app: Flask, blueprint: Blueprint):
        if cls.enable_url_lang_code_prefix:
            url_prefix = (blueprint.url_prefix or '').rstrip('/')
            app.register_blueprint(blueprint, url_prefix=cls.get_url_rule(url_prefix))

    @classmethod
    def add_url_rule(cls, app: Flask, rule: str, **kwargs):
        if cls.enable_url_lang_code_prefix:
            app.add_url_rule(cls.get_url_rule(rule), **kwargs)

    @classmethod
    def get_locale(cls):
        languages = current_app.config['LANGUAGES']
        return g.get(cls.language_code_key,
                     request.accept_languages.best_match(languages))

    @classmethod
    def set_url_defaults(cls, endpoint: str, values: Dict[str, Any]):
        if cls.language_code_key in values or not g.get(cls.language_code_key, None):
            return

        if current_app.url_map.is_endpoint_expecting(endpoint, cls.language_code_key):
            values[cls.language_code_key] = g.lang_code

    @classmethod
    def lang_code_url_value_preprocessor(cls, endpoint: str, values: Dict[str, Any]):
        if values is not None:
            g.lang_code = values.pop(cls.language_code_key, None)

    @classmethod
    def before_init_app(cls, app: Flask):
        babel.locale_selector_func = cls.get_locale
        if cls.enable_url_lang_code_prefix:
            app.url_value_preprocessor(cls.lang_code_url_value_preprocessor)
            app.url_defaults(cls.set_url_defaults)

    @classmethod
    def after_init_app(cls, app: Flask):
        if not app.config.get('LAZY_TRANSLATIONS'):
            app.jinja_env.install_gettext_callables(gettext, ngettext, newstyle=True)
        else:
            app.jinja_env.install_gettext_callables(lazy_gettext, lazy_ngettext,
                                                    newstyle=True)


def gettext(*args, **kwargs):
    key = args[0]
    key_match = TRANSLATION_KEY_RE.match(key)
    translation = _gettext(*args, **kwargs)
    if not key_match or translation != key:
        return translation

    return _get_domain(key_match).gettext(*args, **kwargs)


def lazy_gettext(*args, **kwargs):
    return make_lazy_string(gettext, *args, **kwargs)


def ngettext(*args, **kwargs):
    is_plural = args[2] > 1
    if not is_plural:
        key = args[0]
        key_match = TRANSLATION_KEY_RE.match(key)
    else:
        key = args[1]
        key_match = PLURAL_TRANSLATION_KEY_RE.match(key)

    translation = _ngettext(*args, **kwargs)
    if not key_match or translation != key:
        return translation

    return _get_domain(key_match).ngettext(*args, **kwargs)


def lazy_ngettext(*args, **kwargs):
    return make_lazy_string(ngettext, *args, **kwargs)


def _get_domain(match):
    domain_name = match.groupdict()['domain']
    try:
        domain_resources = pkg_resources.resource_filename(domain_name, 'translations')
    except ImportError:
        return current_app.extensions['babel']._default_domain

    return Domain(domain_resources, domain=domain_name)


_ = LocalProxy(
    lambda: lazy_gettext if current_app.config.get('LAZY_TRANSLATIONS') else gettext)
