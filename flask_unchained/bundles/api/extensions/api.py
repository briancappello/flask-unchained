from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec.ext.marshmallow.openapi import __location_map__
from apispec_webframeworks.flask import FlaskPlugin

from flask_unchained import FlaskUnchained, unchained
from flask_unchained.bundles.controller.constants import (
    CREATE, DELETE, GET, LIST, PATCH, PUT)
from flask_unchained.string_utils import title_case, pluralize

from ..model_resource import ModelResource


class Api:
    """
    The `Api` extension::

        from flask_unchained.bundles.api import api

    Allows interfacing with `apispec <https://apispec.readthedocs.io/en/latest/>`_.
    """

    def __init__(self):
        self.app: FlaskUnchained = None
        self.flask_plugin: FlaskPlugin = None
        self.ma_plugin: MarshmallowPlugin = None
        self.spec: APISpec = None

    def init_app(self, app: FlaskUnchained):
        self.app = app
        app.extensions['api'] = self

        plugins = app.config.API_APISPEC_PLUGINS
        plugins = plugins and list(plugins) or []
        self.flask_plugin = FlaskPlugin()
        self.ma_plugin = MarshmallowPlugin()
        plugins.extend([self.flask_plugin, self.ma_plugin])

        self.spec = APISpec(title=app.config.API_TITLE or app.name,
                            version=app.config.API_VERSION,
                            openapi_version=app.config.API_OPENAPI_VERSION,
                            plugins=plugins,
                            info=dict(description=app.config.API_DESCRIPTION))

    def register_serializer(self, serializer, name=None, **kwargs):
        """
        Method to manually register a :class:`Serializer` with APISpec.

        :param serializer:
        :param name:
        :param kwargs:
        """
        name = name or serializer.__name__
        if name not in self.spec.components.schemas:
            self.spec.components.schema(name, schema=serializer, **kwargs)

    # FIXME need to be able to create 'fake' schemas for the query parameter
    def register_model_resource(self, resource: ModelResource):
        """
        Method to manually register a :class:`ModelResource` with APISpec.

        :param resource:
        """
        model_name = resource.Meta.model.__name__
        self.spec.tag({
            'name': model_name,
            'description': resource.Meta.model.__doc__,
        })

        for method in resource.methods():
            key = f'{resource.__name__}.{method}'
            if key not in unchained.controller_bundle.controller_endpoints:
                continue

            docs = {}
            http_method = method

            if method == CREATE:
                http_method = 'post'
                docs[http_method] = dict(
                    parameters=[{
                        'in': __location_map__['json'],
                        'required': True,
                        'schema': resource.Meta.serializer_create,
                    }],
                    responses={
                        '201': dict(description=getattr(resource, CREATE).__doc__,
                                    schema=resource.Meta.serializer_create),
                    },
                )
            elif method == DELETE:
                docs[http_method] = dict(
                    parameters=[],
                    responses={
                        '204': dict(description=getattr(resource, DELETE).__doc__),
                    },
                )
            elif method == GET:
                docs[http_method] = dict(
                    parameters=[],
                    responses={
                        '200': dict(description=getattr(resource, GET).__doc__,
                                    schema=resource.Meta.serializer),
                    },
                )
            elif method == LIST:
                http_method = 'get'
                docs[http_method] = dict(
                    parameters=[],
                    responses={
                        '200': dict(description=getattr(resource, LIST).__doc__,
                                    schema=resource.Meta.serializer_many),
                    },
                )
            elif method == PATCH:
                docs[http_method] = dict(
                    parameters=[{
                        'in': __location_map__['json'],
                        'required': False,
                        'schema': resource.Meta.serializer,
                    }],
                    responses={
                        '200': dict(description=getattr(resource, PATCH).__doc__,
                                    schema=resource.Meta.serializer),
                    },
                )
            elif method == PUT:
                docs[http_method] = dict(
                    parameters=[{
                        'in': __location_map__['json'],
                        'required': True,
                        'schema': resource.Meta.serializer,
                    }],
                    responses={
                        '200': dict(description=getattr(resource, PUT).__doc__,
                                    schema=resource.Meta.serializer),
                    },
                )

            docs[http_method]['tags'] = [model_name]
            display_name = title_case(model_name)
            if method == LIST:
                display_name = pluralize(display_name)
            docs[http_method]['summary'] = f'{http_method.upper()} {display_name}'

            routes = unchained.controller_bundle.controller_endpoints[key]
            for route in routes:
                for rule in self.app.url_map.iter_rules(route.endpoint):
                    self.spec.path(app=self.app, rule=rule, operations=docs,
                                   view=route.view_func)

    def register_field(self, field, *args):
        """
        Register custom Marshmallow field.

        Registering the Field class allows the Schema parser to set the proper
        type and format when documenting parameters from Schema fields.

        :param Field field: Marshmallow Field class
        :param: args:
            - a pair of the form ``(type, format)`` to map to
            - a core marshmallow field type (then that type's mapping is used)

        Examples::

            # Map to ('string', 'UUID')
            api.register_field(UUIDField, 'string', 'UUID')
            # Map to ('string')
            api.register_field(URLField, 'string', None)
            # Map to ('integer, 'int32')
            api.register_field(CustomIntegerField, ma.fields.Integer)
        """
        self.ma_plugin.map_to_openapi_type(*args)(field)
