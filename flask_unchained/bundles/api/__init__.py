"""
    flask_unchained.bundles.api
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Adds RESTful API support to Flask Unchained

    :copyright: Copyright © 2018 Brian Cappello
    :license: MIT, see LICENSE for more details
"""

__version__ = '0.2.2'

import enum

from flask import Flask
from flask_unchained import Bundle, unchained
from speaklater import _LazyString

from .extensions import api, ma
from .model_resource import ModelResource


class ApiBundle(Bundle):
    # the template folder gets set manually by the OpenAPI bp
    template_folder = None

    @classmethod
    def after_init_app(cls, app: Flask):
        cls.set_json_encoder(app)
        app.before_first_request(cls.register_model_resources)

    @classmethod
    def register_model_resources(cls):
        for resource in unchained.api_bundle.resources_by_model.values():
            api.register_model_resource(resource)

    @classmethod
    def set_json_encoder(cls, app: Flask):
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

                api_store = unchained.api_bundle
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
