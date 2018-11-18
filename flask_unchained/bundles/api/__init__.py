import enum

from flask_unchained import Bundle, FlaskUnchained, unchained
from speaklater import _LazyString

from .extensions import Api, Marshmallow, api, ma
from .model_resource import ModelResource
from .model_serializer import ModelSerializer, _Unmarshaller


class ApiBundle(Bundle):
    def __init__(self):
        self.resources_by_model = {}
        """
        Lookup of resource classes by class name.
        """

        self.serializers = {}
        """
        Lookup of serializer classes by class name.
        """

        self.serializers_by_model = {}
        """
        Lookup of serializer classes by model class name
        """

        self.create_by_model = {}
        """
        Lookup of serializer classes by model class name, as set by
        ``@ma.serializer(create=True)`` (see
        :meth:`~flask_unchained.bundles.api.extensions.Marshmallow.serializer`)
        """

        self.many_by_model = {}
        """
        Lookup of serializer classes by model class name, as set by
        ``@ma.serializer(many=True)`` (see
        :meth:`~flask_unchained.bundles.api.extensions.Marshmallow.serializer`)
        """

    # the template folder gets set manually by the OpenAPI bp
    template_folder = None

    def before_init_app(self, app: FlaskUnchained):
        try:
            from marshmallow import marshalling
            setattr(marshalling, 'Unmarshaller', _Unmarshaller)
        except ImportError:
            return

    def after_init_app(self, app: FlaskUnchained):
        """
        Configure the JSON encoder for Flask to be able to serialize Enums,
        LocalProxy objects, and SQLAlchemy models.
        """
        self.set_json_encoder(app)
        app.before_first_request(self.register_model_resources)

    def register_model_resources(self):
        for resource in unchained.api_bundle.resources_by_model.values():
            api.register_model_resource(resource)

    def set_json_encoder(self, app: FlaskUnchained):
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

                api_bundle = unchained.api_bundle
                if isinstance(obj, BaseModel):
                    model_name = obj.__class__.__name__
                    serializer_cls = api_bundle.serializers_by_model.get(model_name)
                    if serializer_cls:
                        return serializer_cls().dump(obj).data

                elif (obj and isinstance(obj, (list, tuple))
                        and isinstance(obj[0], BaseModel)):
                    model_name = obj[0].__class__.__name__
                    serializer_cls = api_bundle.many_by_model.get(
                        model_name,
                        api_bundle.serializers_by_model.get(model_name))
                    if serializer_cls:
                        return serializer_cls(many=True).dump(obj).data

                return super().default(obj)

        app.json_encoder = JSONEncoder
