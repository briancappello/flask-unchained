import enum

from flask_unchained import Bundle, FlaskUnchained, unchained
from flask_unchained._compat import is_local_proxy
from speaklater import _LazyString

from .extensions import Api, Marshmallow, api, ma
from .model_resource import ModelResource
from .model_serializer import ModelSerializer
from .views import OpenAPIController


class ApiBundle(Bundle):
    """The API Bundle."""

    name = 'api_bundle'
    """
    The name of the API Bundle.
    """

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

    def after_init_app(self, app: FlaskUnchained):
        """
        Configure the JSON encoder for Flask to be able to serialize Enums,
        LocalProxy objects, and SQLAlchemy models.
        """
        from flask_unchained.bundles.sqlalchemy import BaseModel

        class JSONEncoder(app.json_encoder):
            def default(self, obj):
                if is_local_proxy(obj):
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
                        return serializer_cls().dump(obj)

                elif (obj and isinstance(obj, (list, tuple))
                        and isinstance(obj[0], BaseModel)):
                    model_name = obj[0].__class__.__name__
                    serializer_cls = api_bundle.many_by_model.get(
                        model_name,
                        api_bundle.serializers_by_model.get(model_name))
                    if serializer_cls:
                        return serializer_cls(many=True).dump(obj)

                return super().default(obj)

        app.json_encoder = JSONEncoder
