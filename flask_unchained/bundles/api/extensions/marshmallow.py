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
        self.Decimal = ma.fields.Decimal
        self.Dict = ma.fields.Dict
        self.Email = ma.fields.Email
        self.Field = ma.fields.Field
        self.Float = ma.fields.Float
        self.FormattedString = ma.fields.FormattedString
        self.Function = ma.fields.Function
        self.Int = ma.fields.Int
        self.Integer = ma.fields.Integer
        self.List = ma.fields.List
        self.LocalDateTime = ma.fields.LocalDateTime
        self.Method = ma.fields.Method
        self.Nested = ma.fields.Nested
        self.Number = ma.fields.Number
        self.Raw = ma.fields.Raw
        self.Str = ma.fields.Str
        self.String = ma.fields.String
        self.Time = ma.fields.Time
        self.TimeDelta = ma.fields.TimeDelta
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
