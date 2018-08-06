"""
    API Bundle
    ----------

    Adds RESTful API support to Flask Unchained
"""

import enum

from flask import Flask
from flask_unchained import Bundle, unchained
from flask_unchained.utils import AttrDict
from speaklater import _LazyString

from .extensions import api, ma
from .model_resource import ModelResource


class ApiBundle(Bundle):
    def __init__(self):
        self.store = AttrDict(
            # model class name -> resource class
            resources_by_model={},

            # serializer class name -> serializer class
            serializers={},

            # model class name -> serializer class (serializer.__kind__ == 'all')
            serializers_by_model={},

            # model class name -> serializer class (serializer.__kind__ == 'create')
            create_by_model={},

            # model class name -> serializer class (serializer.__kind__ == 'many')
            many_by_model={},
        )

    # the template folder gets set manually by the OpenAPI bp
    template_folder = None

    def after_init_app(self, app: Flask):
        self.set_json_encoder(app)
        app.before_first_request(self.register_model_resources)

    def register_model_resources(self):
        for resource in unchained.api_bundle.store.resources_by_model.values():
            api.register_model_resource(resource)

    def set_json_encoder(self, app: Flask):
        from flask_unchained.bundles.sqlalchemy import BaseModel
        from flask_unchained import unchained
        from werkzeug.local import LocalProxy

        class JSONEncoder(app.json_encoder):
            def default(self, obj):
                if isinstance(obj, LocalProxy):
                    obj = obj._get_current_object()

                if isinstance(obj, enum.Enum):
                    return obj.name
                elif isinstance(obj, _LazyString):
                    return str(obj)

                api_store = unchained.api_bundle.store
                if isinstance(obj, BaseModel):
                    model_name = obj.__class__.__name__
                    serializer_cls = api_store.serializers_by_model.get(model_name)
                    if serializer_cls:
                        return serializer_cls().dump(obj).data

                elif (obj and isinstance(obj, (list, tuple))
                        and isinstance(obj[0], BaseModel)):
                    model_name = obj[0].__class__.__name__
                    serializer_cls = api_store.many_by_model.get(
                        model_name,
                        api_store.serializers_by_model.get(model_name))
                    if serializer_cls:
                        return serializer_cls(many=True).dump(obj).data

                return super().default(obj)

        app.json_encoder = JSONEncoder
