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

        super().__init__(
            title=app.config.get('API_TITLE', app.name),
            version=app.config.get('API_VERSION', '1'),
            openapi_version=app.config.get('API_OPENAPI_VERSION', '2.0'),
            info=dict(
                description=app.config.get('API_DESCRIPTION', None),
            ),
            plugins=plugins,
        )
        self.register_routes(app)

    def register_routes(self, app: FlaskUnchained):
        redoc_url_prefix = app.config.get('API_REDOC_URL_PREFIX', '/api-docs').rstrip('/')
        template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        bp = Blueprint('api-docs', __name__, url_prefix=redoc_url_prefix,
                       template_folder=template_folder)

        # Serve json spec at 'url_prefix/openapi.json' by default
        json_path = app.config.get('OPENAPI_JSON_PATH', 'openapi.json')
        bp.add_url_rule(json_path, endpoint='openapi_json', view_func=self._openapi_json)

        # Serve ReDoc at `url_prefix/' by default
        redoc_path = app.config.get('OPENAPI_REDOC_PATH', '/')
        bp.add_url_rule(redoc_path, endpoint='openapi_redoc', view_func=self._openapi_redoc)

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

        The ReDoc script URL can be specified as OPENAPI_REDOC_URL.
        Otherwise, a CDN script is used based on the ReDoc version. The
        version can - and should - be specified as OPENAPI_REDOC_VERSION,
        otherwise, 'latest' is used.
        When using 1.x branch (i.e. when OPENAPI_REDOC_VERSION is "latest" or
        begins with "v1"), GitHub CDN is used.
        When using 2.x branch (i.e. when OPENAPI_REDOC_VERSION is "next" or
        begins with "2" or "v2"), unpkg nmp CDN is used.
        OPENAPI_REDOC_VERSION is ignored when OPENAPI_REDOC_URL is passed.
        """
        redoc_url = self.app.config.get('OPENAPI_REDOC_URL', None)
        redoc_version = self.app.config.get('OPENAPI_REDOC_VERSION', 'next')
        if redoc_url is None:
            redoc_url = (
                'https://cdn.jsdelivr.net/npm/redoc@'
                '{}/bundles/redoc.standalone.js'.format(redoc_version))
        return render_template('redoc.html',
                               title=self.app.config.get('API_TITLE', self.app.name),
                               redoc_url=redoc_url)

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
