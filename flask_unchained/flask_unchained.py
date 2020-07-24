from types import FunctionType
from typing import *

import flask

from .unchained import Unchained, unchained
from .utils import AttrDict


class AttrDictFlaskConfig(AttrDict, flask.Config):
    """
    The config class for Flask Unchained. Implements attribute access for
    config options, eg the following are equivalent::

        # reading values
        secret_key = app.config['SECRET_KEY']
        secret_key = app.config.SECRET_KEY

        # setting values
        app.config['SECRET_KEY'] = 'super-secret'
        app.config.SECRET_KEY = 'super-secret'

    Otherwise the same as :class:`flask.Config`.
    """


class FlaskUnchained(flask.Flask):
    """
    A simple subclass of :class:`flask.Flask`. Overrides
    :meth:`register_blueprint` and :meth:`add_url_rule` to support
    automatic (optional) registration of URLs prefixed with a language code.
    """

    config_class = AttrDictFlaskConfig

    env: str = None
    """
    The environment the application is running in. Will be one of ``development``,
    ``production``, ``staging``, or ``test``.
    """

    # NOTE: the following all get set by ControllerBundle.before_init_app
    # jinja_environment = UnchainedJinjaEnvironment
    # jinja_options = {**app.jinja_options,
    #                  'loader': UnchainedJinjaLoader(app)}
    # jinja_env.globals['url_for'] = url_for

    unchained: Unchained = unchained
    """
    The :class:`~flask_unchained.Unchained` extension instance.
    """

    def register_blueprint(self,
                           blueprint: flask.Blueprint,
                           *,
                           register_with_babel: bool = True,
                           **options: Any,
                           ) -> None:
        """
        The same as :meth:`flask.Flask.register_blueprint`, but if
        ``register_with_babel`` is True, then we also allow the Babel Bundle an
        opportunity to register language code prefixed URLs.
        """
        if self.unchained.babel_bundle and register_with_babel:
            self.unchained.babel_bundle.register_blueprint(self, blueprint, **options)
        super().register_blueprint(blueprint, **options)

    def add_url_rule(self,
                     rule: str,
                     endpoint: Optional[str] = None,
                     view_func: Optional[FunctionType] = None,
                     provide_automatic_options: Optional[bool] = None,
                     *,
                     register_with_babel: bool = False,
                     **options: Any,
                     ) -> None:
        """
        The same as :meth:`flask.Flask.add_url_rule`, but if ``register_with_babel``
        is True, then we also allow the Babel Bundle an opportunity to register a
        language code prefixed URL.
        """
        if self.unchained.babel_bundle and register_with_babel:
            self.unchained.babel_bundle.add_url_rule(
                self, rule, endpoint=endpoint, view_func=view_func,
                provide_automatic_options=provide_automatic_options, **options)
        super().add_url_rule(
            rule, endpoint=endpoint, view_func=view_func,
            provide_automatic_options=provide_automatic_options, **options)

    def __str__(self):
        return f"<FlaskUnchained module={self.import_name!r}>"

    def __repr__(self):
        return self.__str__()


__all__ = [
    'FlaskUnchained',
]
