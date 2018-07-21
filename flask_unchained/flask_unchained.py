from flask import Flask

from .unchained import Unchained, unchained


class FlaskUnchained(Flask):
    unchained: Unchained = unchained

    def register_blueprint(self, blueprint, **options):
        unchained.babel_bundle.register_blueprint(self, blueprint, **options)
        return super().register_blueprint(blueprint, **options)

    def add_url_rule(self, rule, endpoint=None, view_func=None,
                     provide_automatic_options=None, **options):
        unchained.babel_bundle.add_url_rule(
            self, rule, endpoint=endpoint, view_func=view_func,
            provide_automatic_options=provide_automatic_options, **options)
        return super().add_url_rule(rule, endpoint, view_func,
                                    provide_automatic_options, **options)
