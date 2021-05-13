import apispec

from apispec_webframeworks.flask import FlaskPlugin
from apispec.ext.marshmallow import MarshmallowPlugin as BaseMarshmallowPlugin

from .openapi_converter import OpenAPIConverter


class MarshmallowPlugin(BaseMarshmallowPlugin):
    def init_spec(self, spec):
        super().init_spec(spec)
        self.openapi = OpenAPIConverter(openapi_version=spec.openapi_version)


class APISpec(apispec.APISpec):
    def __init__(self, title, version, openapi_version, plugins=(), **options):
        plugins = plugins and list(plugins) or []
        self.flask_plugin = FlaskPlugin()
        self.ma_plugin = MarshmallowPlugin()
        plugins.extend([self.flask_plugin, self.ma_plugin])

        super().__init__(title=title,
                         version=version,
                         openapi_version=openapi_version,
                         plugins=plugins,
                         **options)

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
