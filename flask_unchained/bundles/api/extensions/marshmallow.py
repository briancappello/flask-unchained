from flask import Flask

try:
    import marshmallow as ma
    import flask_marshmallow as flask_ma
    from flask_marshmallow.sqla import HyperlinkRelated
except ImportError:
    from py_meta_utils import OptionalClass as ma
    from py_meta_utils import OptionalClass as flask_ma
    from py_meta_utils import OptionalClass as HyperlinkRelated

from ..model_serializer import ModelSerializer


class Marshmallow:
    """
    The `Marshmallow` extension::

        from flask_unchained.bundles.api import ma

    Allows decorating a :class:`~flask_unchained.bundles.api.ModelSerializer`
    with :meth:`serializer` to specify it should be used for creating objects,
    listing them, or as the fallback.

    Also provides aliases from the following modules:

    **flask_unchained.bundles.api**

    .. autosummary::

        ~flask_unchained.bundles.api.ModelSerializer

    **marshmallow.decorators**

    .. autosummary::

        ~marshmallow.decorators.pre_load
        ~marshmallow.decorators.post_load
        ~marshmallow.decorators.pre_dump
        ~marshmallow.decorators.post_dump
        ~marshmallow.decorators.validates
        ~marshmallow.decorators.validates_schema

    **marshmallow.exceptions**

    .. autosummary::

        ~marshmallow.exceptions.ValidationError

    **marshmallow.fields**

    .. autosummary::

        # alias marshmallow fields
        ~marshmallow.fields.Bool
        ~marshmallow.fields.Boolean
        ~marshmallow.fields.Constant
        ~marshmallow.fields.Date
        ~marshmallow.fields.DateTime
        ~marshmallow.fields.NaiveDateTime
        ~marshmallow.fields.AwareDateTime
        ~marshmallow.fields.Decimal
        ~marshmallow.fields.Dict
        ~marshmallow.fields.Email
        ~marshmallow.fields.Field
        ~marshmallow.fields.Float
        ~marshmallow.fields.Function
        ~marshmallow.fields.Int
        ~marshmallow.fields.Integer
        ~marshmallow.fields.List
        ~marshmallow.fields.Mapping
        ~marshmallow.fields.Method
        ~marshmallow.fields.Nested
        ~marshmallow.fields.Number
        ~marshmallow.fields.Pluck
        ~marshmallow.fields.Raw
        ~marshmallow.fields.Str
        ~marshmallow.fields.String
        ~marshmallow.fields.Time
        ~marshmallow.fields.TimeDelta
        ~marshmallow.fields.Tuple
        ~marshmallow.fields.UUID
        ~marshmallow.fields.Url
        ~marshmallow.fields.URL

    **flask_marshmallow.fields**

    .. autosummary::

        ~flask_marshmallow.fields.AbsoluteUrlFor
        ~flask_marshmallow.fields.AbsoluteURLFor
        ~flask_marshmallow.fields.UrlFor
        ~flask_marshmallow.fields.URLFor
        ~flask_marshmallow.fields.Hyperlinks

    **flask_marshmallow.sqla**

    .. autosummary::

        ~flask_marshmallow.sqla.HyperlinkRelated
    """

    def __init__(self):
        self.Serializer = flask_ma.Schema
        self.ModelSerializer = ModelSerializer

        # alias marshmallow stuffs
        self.pre_load = ma.pre_load
        self.post_load = ma.post_load
        self.pre_dump = ma.pre_dump
        self.post_dump = ma.post_dump
        self.validates = ma.validates
        self.validates_schema = ma.validates_schema
        self.ValidationError = ma.ValidationError

        # alias marshmallow fields
        self.Bool = ma.fields.Bool
        self.Boolean = ma.fields.Boolean
        self.Constant = ma.fields.Constant
        self.Date = ma.fields.Date
        self.DateTime = ma.fields.DateTime
        self.NaiveDateTime = ma.fields.NaiveDateTime
        self.AwareDateTime = ma.fields.AwareDateTime
        self.Decimal = ma.fields.Decimal
        self.Dict = ma.fields.Dict
        self.Email = ma.fields.Email
        self.Field = ma.fields.Field
        self.Float = ma.fields.Float
        self.Function = ma.fields.Function
        self.Int = ma.fields.Int
        self.Integer = ma.fields.Integer
        self.List = ma.fields.List
        self.Mapping = ma.fields.Mapping
        self.Method = ma.fields.Method
        self.Nested = ma.fields.Nested
        self.Number = ma.fields.Number
        self.Pluck = ma.fields.Pluck
        self.Raw = ma.fields.Raw
        self.Str = ma.fields.Str
        self.String = ma.fields.String
        self.Time = ma.fields.Time
        self.TimeDelta = ma.fields.TimeDelta
        self.Tuple = ma.fields.Tuple
        self.UUID = ma.fields.UUID
        self.Url = ma.fields.Url
        self.URL = ma.fields.URL

        # alias flask_marshmallow fields
        self.AbsoluteUrlFor = flask_ma.fields.AbsoluteUrlFor
        self.AbsoluteURLFor = flask_ma.fields.AbsoluteURLFor
        self.UrlFor = flask_ma.fields.UrlFor
        self.URLFor = flask_ma.fields.URLFor
        self.Hyperlinks = flask_ma.fields.Hyperlinks
        self.HyperlinkRelated = HyperlinkRelated

    def init_app(self, app: Flask):
        db = app.extensions['sqlalchemy'].db
        self.ModelSerializer.OPTIONS_CLASS.session = db.session
        app.extensions['ma'] = self

    def serializer(self, create=False, many=False):
        """
        Decorator to mark a :class:`Serializer` subclass for a specific purpose, ie,
        to be used during object creation **or** for serializing lists of objects.

        :param create: Whether or not this serializer is for object creation.
        :param many: Whether or not this serializer is for lists of objects.
        """
        if create and many:
            raise Exception('Can only set one of `create` or `many` to `True`')

        def wrapper(cls):
            cls.__kind__ = (create and 'create'
                            or many and 'many'
                            or 'all')
            return cls
        return wrapper
