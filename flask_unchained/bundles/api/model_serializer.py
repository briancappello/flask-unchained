from types import FunctionType
from typing import *

from flask_unchained import unchained
from flask_unchained.di import _set_up_class_dependency_injection
from flask_unchained.string_utils import title_case
from py_meta_utils import McsArgs
from speaklater import _LazyString

try:
    from flask_marshmallow.sqla import (
        SQLAlchemyAutoSchema as BaseModelSerializer,
        SQLAlchemyAutoSchemaOpts as BaseModelSerializerOptionsClass)
    from marshmallow.fields import Field
    from marshmallow.class_registry import _registry
    from marshmallow.exceptions import ValidationError as MarshmallowValidationError
    from marshmallow_sqlalchemy.convert import ModelConverter as BaseModelConverter
    from marshmallow_sqlalchemy.schema.sqlalchemy_schema import (
        SQLAlchemyAutoSchemaMeta as BaseModelSerializerMetaclass)
    from sqlalchemy.orm import SynonymProperty
except ImportError:
    _registry = {}
    from py_meta_utils import OptionalClass as BaseModelSerializer
    from py_meta_utils import OptionalClass as BaseModelSerializerOptionsClass
    from py_meta_utils import OptionalClass as MarshmallowValidationError
    from py_meta_utils import OptionalClass as BaseModelConverter
    from py_meta_utils import OptionalMetaclass as BaseModelSerializerMetaclass

from .config import Config


class ModelConverter(BaseModelConverter):
    def fields_for_model(self,
                         model,
                         *,
                         include_fk=False,
                         include_relationships=False,
                         fields=None,
                         exclude=None,
                         base_fields=None,
                         dict_cls=dict):
        """
        Overridden to correctly name hybrid_property fields, eg given::

            class User(db.Model):
                _password = db.Column('password', db.String)

                @db.hybrid_property
                def password(self):
                    return self._password

                @password.setter
                def password(self, password):
                    self._password = hash_password(password)

        In this case upstream marshmallow_sqlalchemy uses '_password' for the
        field name, but we use 'password', as would be expected because it's
        the attribute name used for the public interface of the Model. In order
        for this logic to work, the column name must be specified and it must be
        the same as the hybrid property name. Otherwise we just fallback to the
        upstream naming convention.
        """
        # this prevents an error when building the docs
        if not hasattr(model, '__mapper__'):
            return

        result = dict_cls()
        base_fields = base_fields or {}
        for prop in model.__mapper__.iterate_properties:
            key = self._get_field_name(prop)
            if self._should_exclude_field(prop, fields=fields, exclude=exclude):
                result[key] = None
                continue
            if isinstance(prop, SynonymProperty):
                continue
            if hasattr(prop, 'columns'):
                if not include_fk:
                    # Only skip a column if there is no overridden column
                    # which does not have a Foreign Key.
                    for column in prop.columns:
                        if not column.foreign_keys:
                            break
                    else:
                        continue

                col_name = prop.columns[0].name
                if key != col_name and hasattr(model, col_name):
                    key = col_name

            if not include_relationships and hasattr(prop, "direction"):
                continue

            field = base_fields.get(key) or self.property2field(prop)
            if field:
                result[key] = field

        return result

    def property2field(self, prop, instance=True, field_class=None, **kwargs):
        """
        Overridden to mark non-nullable model columns as required (unless it's the
        primary key, because there's no way to tell if we're generating fields
        for a create or an update).
        """
        field = super().property2field(prop, instance=instance, field_class=field_class, **kwargs)
        # when a column is not nullable, mark the field as required
        if hasattr(prop, 'columns'):
            col = prop.columns[0]
            if not col.primary_key and not col.nullable:
                field.required = True
        return field


class _ModelDescriptor:
    def __get__(self, instance, owner):
        # make sure to always return the correct mapped model class
        if not unchained._models_initialized or not instance._model:
            return instance._model
        return unchained.sqlalchemy_bundle.models[instance._model.__name__]

    def __set__(self, instance, value):
        instance._model = value


class _ModelSerializerMetaMetaclass(type):
    model = _ModelDescriptor()


class _ModelSerializerMeta(metaclass=_ModelSerializerMetaMetaclass):
    pass


class ModelSerializerMetaclass(BaseModelSerializerMetaclass):
    def __new__(mcs, name, bases, clsdict):
        mcs_args = McsArgs(mcs, name, bases, clsdict)
        _set_up_class_dependency_injection(mcs_args)
        if mcs_args.is_abstract:
            return super().__new__(*mcs_args)

        meta = mcs_args.getattr('Meta', None)
        model_missing = False
        try:
            if meta.model is None:
                model_missing = True
        except AttributeError:
            model_missing = True

        if model_missing:
            raise AttributeError(f'{name} is missing the ``class Meta`` model attribute')

        model = meta.model
        try:
            model = unchained.sqlalchemy_bundle.models[meta.model.__name__]
        except AttributeError as e:
            # this happens when attempting to generate documentation and the
            # sqlalchemy bundle hasn't been loaded
            safe_error = "'DeferredBundleBlueprintFunctions' object has no attribute 'models'"
            if safe_error not in str(e):
                raise e
        except KeyError:
            pass

        meta_dict = dict(meta.__dict__)

        additional_fields = meta_dict.pop('additional', None)
        if additional_fields:
            fields = [name for name, field in clsdict.items()
                      if isinstance(field, Field)]
            meta_dict['fields'] = fields + list(additional_fields)

        meta_dict.pop('model', None)
        clsdict['Meta'] = type('Meta', (_ModelSerializerMeta,), meta_dict)
        clsdict['Meta'].model = model

        return super().__new__(*mcs_args)

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if name and cls.opts and cls.opts.register and name in _registry:
            for existing_cls in _registry[name]:
                fullname = f'{existing_cls.__module__}.{existing_cls.__name__}'
                _registry.pop(fullname, None)
            fullname = f'{cls.__module__}.{cls.__name__}'
            _registry[name] = _registry[fullname] = [cls]

    @classmethod
    def get_declared_fields(mcs, klass, cls_fields, inherited_fields, dict_cls):
        # overridden to fix building the docs
        try:
            return super().get_declared_fields(klass, cls_fields, inherited_fields, dict_cls)
        except TypeError:
            pass


class ModelSerializerOptionsClass(BaseModelSerializerOptionsClass):
    """
    Sets the default ``model_converter`` to :class:`_ModelConverter`.
    """
    def __init__(self, meta, **kwargs):
        self._model = None
        self.dump_key_fn = getattr(meta, 'dump_key_fn', Config.DUMP_KEY_FN)
        self.load_key_fn = getattr(meta, 'load_key_fn', Config.LOAD_KEY_FN)

        # override the upstream default values for load_instance and model_converter
        meta.load_instance = getattr(meta, 'load_instance', True)
        meta.model_converter = getattr(meta, 'model_converter', ModelConverter)
        super().__init__(meta, **kwargs)

    @property
    def model(self):
        # make sure to always return the correct mapped model class
        if not unchained._models_initialized or not self._model:
            return self._model
        return unchained.sqlalchemy_bundle.models[self._model.__name__]

    @model.setter
    def model(self, model):
        self._model = model


def maybe_convert_keys(data: Any,
                       key_fn: Optional[FunctionType] = None,
                       fields: Tuple[str] = (),
                       many: bool = False,
                       ) -> Any:
    if not key_fn or not fields:
        return data

    if many:
        return [maybe_convert_keys(el, key_fn, fields, many=False) for el in data]
    elif isinstance(data, dict):
        rv = data.copy()
        for k, v in data.items():
            new_k = key_fn(k)
            if k not in fields and new_k not in fields:
                continue
            if k != new_k:
                rv.pop(k)
            rv[new_k] = v
        return rv
    return data


class ModelSerializer(BaseModelSerializer, metaclass=ModelSerializerMetaclass):
    """
    Base class for SQLAlchemy model serializers. This is pretty much a stock
    :class:`flask_marshmallow.sqla.ModelSchema`, except:

    - dependency injection is set up automatically on ModelSerializer
    - when loading to update an existing instance, validate the primary keys are the same
    - automatically make fields named ``slug``, ``model.Meta.created_at``, and
      ``model.Meta.updated_at`` dump-only

    For example::

        from flask_unchained.bundles.api import ModelSerializer
        from flask_unchained.bundles.security.models import Role

        class RoleSerializer(ModelSerializer):
            class Meta:
                model = Role

    Is roughly equivalent to::

        from marshmallow import Schema, fields

        class RoleSerializer(Schema):
            id = fields.Integer(dump_only=True)
            name = fields.String()
            description = fields.String()
            created_at = fields.DateTime(dump_only=True)
            updated_at = fields.DateTime(dump_only=True)
    """
    __abstract__ = True

    OPTIONS_CLASS = ModelSerializerOptionsClass
    opts: ModelSerializerOptionsClass = None  # set by the metaclass

    def is_create(self):
        """
        Check if we're creating a new object. Note that this context flag
        must be set from the outside, ie when the class gets instantiated.
        """
        return self.context.get('is_create', False)

    def load(
        self,
        data: Mapping,
        *,
        many: bool = None,
        partial: Union[bool, Sequence[str], Set[str]] = None,
        unknown: str = None,
        **kwargs,
    ):
        """Deserialize a dict to an object defined by this ModelSerializer's fields.

        A :exc:`ValidationError <marshmallow.exceptions.ValidationError>` is raised
        if invalid data is passed.

        :param data: The data to deserialize.
        :param many: Whether to deserialize `data` as a collection. If `None`, the
            value for `self.many` is used.
        :param partial: Whether to ignore missing fields and not require
            any fields declared. Propagates down to ``Nested`` fields as well. If
            its value is an iterable, only missing fields listed in that iterable
            will be ignored. Use dot delimiters to specify nested fields.
        :param unknown: Whether to exclude, include, or raise an error for unknown
            fields in the data. Use `EXCLUDE`, `INCLUDE` or `RAISE`.
            If `None`, the value for `self.unknown` is used.
        :return: Deserialized data
        """
        # when data is None, which happens when a POST request was made with an
        # empty body, convert it to an empty dict. makes validation errors work
        # as expected
        data = data or {}

        # maybe convert all keys in data with the configured fn
        data = maybe_convert_keys(
            data,
            self.opts.load_key_fn,
            self.opts.fields or set(self.declared_fields.keys()),
            many=many,
        )
        try:
            return super().load(data, many=many, partial=partial, unknown=unknown,
                                **kwargs)
        except MarshmallowValidationError as e:
            e.messages = maybe_convert_keys(
                e.messages,
                self.opts.dump_key_fn,
                self.opts.fields or set(self.declared_fields.keys()),
                many=False,
            )
            raise e

    def dump(self, obj, *, many: bool = None):
        """Serialize an object to native Python data types according to this
        ModelSerializer's fields.

        :param obj: The object to serialize.
        :param many: Whether to serialize `obj` as a collection. If `None`, the value
            for `self.many` is used.
        :return: A dict of serialized data
        :rtype: dict
        """
        data = super().dump(obj, many=many)

        # maybe convert all keys in data with the configured fn
        return maybe_convert_keys(
            data,
            self.opts.dump_key_fn,
            fields=self.opts.fields or set(self.declared_fields.keys()),
            many=many,
        )

    def handle_error(self,
                     error: MarshmallowValidationError,
                     data: Any,  # skipcq: PYL-W0613 (unused arg)
                     **kwargs
                     ) -> None:
        """
        Customize the error messages for required/not-null validators with
        dynamically generated field names. This is definitely a little hacky (it
        mutates state, uses hardcoded strings), but unsure how better to do it
        """
        required_messages = {'Missing data for required field.',
                             'Field may not be null.'}
        for field_name in error.normalized_messages():
            for i, msg in enumerate(error.messages[field_name]):
                if isinstance(msg, _LazyString):
                    msg = str(msg)
                if msg in required_messages:
                    label = title_case(field_name)
                    error.messages[field_name][i] = f'{label} is required.'

    def _init_fields(self):
        """
        Overridden to:
        - automatically validate ids (primary keys) are the same when updating objects.
        - automatically convert slug, created_at, and updated_at to dump-only fields
        """
        super()._init_fields()

        read_only_fields = {field for field in {
            self.Meta.model.Meta.pk,
            'slug',
            self.Meta.model.Meta.created_at,
            self.Meta.model.Meta.updated_at,
        } if field is not None}

        for name in read_only_fields:
            if name in self.fields:
                field = self.fields[name]
                field.dump_only = True
                self.dump_fields[name] = field
                self.load_fields.pop(name, None)


__all__ = [
    'ModelConverter',
    'ModelSerializer',
    'ModelSerializerMetaclass',
    'ModelSerializerOptionsClass',
]
