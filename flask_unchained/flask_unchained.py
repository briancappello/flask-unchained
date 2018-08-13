from flask import Flask


class FlaskUnchained(Flask):
    """
    A simple subclass of the :class:`~flask.Flask` class. Overrides
    :meth:`register_blueprint` and :meth:`add_url_rule` to support
    automatic (optional) registration of URLs prefixed with a language code.
    """

    env: str = None
    """
    The environment the application is running in. Will be one of ``development``,
    ``production``, ``staging``, or ``test``.
    """

    from .unchained import Unchained, unchained

    unchained: Unchained = unchained
    """
    The Flask Unchained extension instance.
    """

    def register_blueprint(self, blueprint, register_with_babel=True, **options):
        """
        Like :meth:`~flask.Flask.register_blueprint`, but if ``register_with_babel``
        is True, then we also allow the Babel Bundle an opportunity to register language
        code prefixed URLs.
        """
        if self.unchained.babel_bundle and register_with_babel:
            self.unchained.babel_bundle.register_blueprint(self, blueprint, **options)
        return super().register_blueprint(blueprint, **options)

    def add_url_rule(self, rule, endpoint=None, view_func=None,
                     provide_automatic_options=None, register_with_babel=False,
                     **options):
        """
        Like :meth:`~flask.Flask.add_url_rule`, but if ``register_with_babel`` is True,
        then we also allow the Babel Bundle an opportunity to register a language code
        prefixed URL.
        """
        if self.unchained.babel_bundle and register_with_babel:
            self.unchained.babel_bundle.add_url_rule(
                self, rule, endpoint=endpoint, view_func=view_func,
                provide_automatic_options=provide_automatic_options, **options)
        return super().add_url_rule(rule, endpoint, view_func,
                                    provide_automatic_options, **options)
