import inspect

from collections import defaultdict
from flask_sqlalchemy.model import Model as FlaskSQLAlchemyBaseModel
from flask_unchained.string_utils import pluralize, title_case
from flask_unchained import lazy_gettext as _
from sqlalchemy.ext.declarative import declared_attr

from .base_query import BaseQuery
from .meta import ModelMetaFactory
from .validation import Required, ValidationError, ValidationErrors


class QueryAliasDescriptor:
    def __get__(self, instance, cls):
        return cls.query


class BaseModel(FlaskSQLAlchemyBaseModel):
    """
    Base model class
    """
    __abstract__ = True
    __validators__ = defaultdict(list)

    class Meta:
        pk = 'id'
        created_at = 'created_at'
        updated_at = 'updated_at'
        polymorphic = False

        # this is strictly for testing meta class stuffs
        _testing_ = 'this setting is only available when ' \
                    'os.getenv("FLASK_ENV") == "test"'

    _meta_factory_class = ModelMetaFactory

    query: BaseQuery
    q: BaseQuery = QueryAliasDescriptor()

    __repr_props__ = ()
    """Set to customize automatic string representation.

    For example::

        class User(database.Model):
            __repr_props__ = ('id', 'email')

            email = Column(String)

        user = User(id=1, email='foo@bar.com')
        print(user)  # prints <User id=1 email="foo@bar.com">
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.update(**kwargs)

    def __repr__(self):
        properties = [f'{prop}={getattr(self, prop)!r}'
                      for prop in self.__repr_props__ if hasattr(self, prop)]
        return f"<{self.__class__.__name__} {' '.join(properties)}>"

    @declared_attr
    def __plural__(self):
        return pluralize(self.__name__)

    @declared_attr
    def __label__(self):
        return title_case(self.__name__)

    @declared_attr
    def __plural_label__(self):
        return title_case(pluralize(self.__name__))

    def update(self, **kwargs):
        """Update fields on the model.

        :param kwargs: The model attribute values to update the model with.
        """
        self.validate(**kwargs)
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return self

    @classmethod
    def validate(cls, partial=True, **kwargs):
        """
        Validate kwargs before setting attributes on the model
        """
        data = kwargs
        if not partial:
            data = dict(**kwargs, **{col.name: None for col in cls.__table__.c
                                     if col.name not in kwargs})

        errors = defaultdict(list)
        for name, value in data.items():
            for validator in cls._get_validators(name):
                try:
                    validator(value)
                except ValidationError as e:
                    e.model = cls
                    e.column = name
                    errors[name].append(str(e))

        if errors:
            raise ValidationErrors(errors)

    @classmethod
    def _get_validators(cls, column_name):
        rv = []
        col = cls.__table__.c.get(column_name)
        validators = cls.__validators__.get(column_name, [])
        for validator in validators:
            if isinstance(validator, str) and hasattr(cls, validator):
                rv.append(getattr(cls, validator))
            else:
                if inspect.isclass(validator):
                    validator = validator()
                rv.append(validator)

        if col is not None:
            not_null = not col.primary_key and not col.nullable
            required_msg = col.info and col.info.get('required', None)
            if not_null or required_msg:
                if isinstance(required_msg, bool):
                    required_msg = None
                elif isinstance(required_msg, str):
                    required_msg = _(required_msg)
                rv.append(Required(required_msg or None))
        return rv

    def __setattr__(self, key, value):
        for validator in self._get_validators(key):
            try:
                validator(value)
            except ValidationError as e:
                e.model = self.__class__
                e.column = key
                raise e
        super().__setattr__(key, value)
