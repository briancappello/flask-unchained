try:
    import apispec
    from apispec.ext.flask import FlaskPlugin
    from apispec.ext.marshmallow import MarshmallowPlugin as BaseMarshmallowPlugin
except ImportError:
    from py_meta_utils import OptionalClass as apispec
    from py_meta_utils import OptionalClass as FlaskPlugin
    from py_meta_utils import OptionalClass as BaseMarshmallowPlugin
import json
import os

from flask import Blueprint, current_app, render_template
from flask_unchained import FlaskUnchained

from .openapi_converter import OpenAPIConverter


class MarshmallowPlugin(BaseMarshmallowPlugin):
    def init_spec(self, spec):
        super().init_spec(spec)
        self.openapi = OpenAPIConverter(openapi_version=spec.openapi_version)


class APISpec(apispec.APISpec):
    def __init__(self, app, *, plugins=None):
        self.app = app

        plugins = plugins and list(plugins) or []
        self.flask_plugin = FlaskPlugin()
        self.ma_plugin = MarshmallowPlugin()
        plugins.extend([self.flask_plugin, self.ma_plugin])

        super().__init__(title=app.config.API_TITLE or app.name,
                         version=app.config.API_VERSION,
                         openapi_version=app.config.API_OPENAPI_VERSION,
                         info=dict(description=app.config.API_DESCRIPTION),
                         plugins=plugins)
        self.register_routes(app)

    # FIXME make a controller for these routes, inject this extension into it
    def register_routes(self, app: FlaskUnchained):
        bp = Blueprint('api-docs', __name__,
                       url_prefix=app.config.API_REDOC_URL_PREFIX.rstrip('/'),
                       template_folder=os.path.join(
                           os.path.dirname(os.path.abspath(__file__)), 'templates'))

        # Serve json spec at `API_REDOC_URL_PREFIX/openapi.json` by default
        bp.add_url_rule(app.config.API_OPENAPI_JSON_PATH,
                        endpoint='openapi_json',
                        view_func=self._openapi_json)

        # Serve ReDoc at `API_REDOC_URL_PREFIX/` by default
        bp.add_url_rule(app.config.API_REDOC_PATH,
                        endpoint='openapi_redoc',
                        view_func=self._openapi_redoc)

        app.register_blueprint(bp, register_with_babel=False)

    def _openapi_json(self):
        """Serve JSON spec file"""
        # We don't use Flask.jsonify here as it would sort the keys
        # alphabetically while we want to preserve the order.
        from pprint import pprint
        pprint(self.to_dict())
        return current_app.response_class(json.dumps(self.to_dict(), indent=4),
                                          mimetype='application/json')

    def _openapi_redoc(self):
        """
        Expose OpenAPI spec with ReDoc

        The ReDoc script URL can be specified as ``API_REDOC_SOURCE_URL``
        """
        return render_template('openapi/redoc.html',
                               title=self.app.config.API_TITLE or self.app.name,
                               redoc_url=self.app.config.API_REDOC_SOURCE_URL)

    def register_converter(self, converter, conv_type, conv_format=None):
        """
        Register custom path parameter converter

        :param BaseConverter converter: Converter.
            Subclass of werkzeug's BaseConverter
        :param str conv_type: Parameter type
        :param str conv_format: Parameter format (optional)
        """
        self.flask_plugin.register_converter(converter, conv_type, conv_format)

    def register_field(self, field, *args):
        """
        Register custom Marshmallow field

        Registering the Field class allows the Schema parser to set the proper
        type and format when documenting parameters from Schema fields.
        :param Field field: Marshmallow Field class
        ``*args`` can be:
        - a pair of the form ``(type, format)`` to map to
        - a core marshmallow field type (then that type's mapping is used)
        """
        self.ma_plugin.map_to_openapi_type(*args)(field)
