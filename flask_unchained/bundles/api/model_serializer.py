from types import FunctionType
from typing import *

from flask_unchained import unchained
from flask_unchained.di import _set_up_class_dependency_injection
from flask_unchained.string_utils import camel_case, snake_case, title_case
from py_meta_utils import McsArgs
from speaklater import _LazyString

try:
    from flask_marshmallow.sqla import (
        ModelSchema as _BaseModelSerializer,
        SchemaOpts as _BaseModelSerializerOptionsClass)
    from marshmallow.class_registry import _registry
    from marshmallow.exceptions import ValidationError as MarshmallowValidationError
    from marshmallow.schema import SchemaMeta as _BaseModelSerializerMetaclass
    from marshmallow_sqlalchemy.convert import ModelConverter as _BaseModelConverter
    from marshmallow_sqlalchemy.schema import (
        ModelSchemaMeta as _BaseModelSchemaMetaclass)
except ImportError:
    _registry = {}
    from py_meta_utils import OptionalClass as _BaseModelSerializer
    from py_meta_utils import OptionalClass as _BaseModelSerializerOptionsClass
    from py_meta_utils import OptionalMetaclass as _BaseModelSerializerMetaclass
    from py_meta_utils import OptionalClass as MarshmallowValidationError
    from py_meta_utils import OptionalClass as _BaseModelConverter
    from py_meta_utils import OptionalMetaclass as _BaseModelSchemaMetaclass


class _ModelConverter(_BaseModelConverter):
    def fields_for_model(self, model, include_fk=False, fields=None,
                         exclude=None, base_fields=None, dict_cls=dict):
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
            if self._should_exclude_field(prop, fields=fields, exclude=exclude):
                result[prop.key] = None
                continue

            attr_name = prop.key
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
                if attr_name != col_name and hasattr(model, col_name):
                    attr_name = col_name

            field = base_fields.get(attr_name) or self.property2field(prop)
            if field:
                result[attr_name] = field
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


class _ModelSerializerMetaclass(_BaseModelSchemaMetaclass):
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
            safe_error = "'DeferredBundleFunctions' object has no attribute 'models'"
            if safe_error not in str(e):
                raise e
        except KeyError:
            pass

        meta_dict = dict(meta.__dict__)
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

    # override marshmallow_sqlalchemy.SchemaMeta.get_declared_fields
    @classmethod
    def get_declared_fields(mcs, klass, cls_fields, inherited_fields, dict_cls):
        """
        Updates declared fields with fields converted from the SQLAlchemy model
        passed as the `model` class Meta option.
        """
        opts = klass.opts
        converter = opts.model_converter(schema_cls=klass)
        base_fields = _BaseModelSerializerMetaclass.get_declared_fields(
            klass, cls_fields, inherited_fields, dict_cls)
        declared_fields = mcs.get_fields(converter, opts, base_fields, dict_cls)
        if declared_fields is not None:  # prevents sphinx from blowing up
            declared_fields.update(base_fields)
        return declared_fields


class _ModelSerializerOptionsClass(_BaseModelSerializerOptionsClass):
    """
    Sets the default ``model_converter`` to :class:`_ModelConverter`.
    """
    def __init__(self, meta, **kwargs):
        self._model = None
        super().__init__(meta, **kwargs)
        self.model_converter = getattr(meta, 'model_converter', _ModelConverter)
        self.dump_key_fn = getattr(meta, 'dump_key_fn', camel_case)
        self.load_key_fn = getattr(meta, 'load_key_fn', snake_case)

    @property
    def model(self):
        # make sure to always return the correct mapped model class
        if not unchained._models_initialized or not self._model:
            return self._model
        return unchained.sqlalchemy_bundle.models[self._model.__name__]

    @model.setter
    def model(self, model):
        self._model = model


def maybe_convert_keys(d: Any, key_fn: Optional[FunctionType] = None):
    if isinstance(d, (list, tuple)):
        return [maybe_convert_keys(el, key_fn) for el in d]
    elif isinstance(d, dict):
        rv = d.copy()
        for k, v in d.items():
            new_k = key_fn(k)
            new_v = maybe_convert_keys(v, key_fn)
            if k != new_k:
                rv.pop(k)
            rv[new_k] = new_v
        return rv
    return d


class ModelSerializer(_BaseModelSerializer, metaclass=_ModelSerializerMetaclass):
    """
    Base class for database model serializers. This is pretty much a stock
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

    OPTIONS_CLASS = _ModelSerializerOptionsClass
    opts: _ModelSerializerOptionsClass = None  # set by the metaclass

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
        data = maybe_convert_keys(data, self.opts.load_key_fn)
        try:
            return super().load(data, many=many, partial=partial, unknown=unknown,
                                **kwargs)
        except MarshmallowValidationError as e:
            e.messages = maybe_convert_keys(e.messages, self.opts.dump_key_fn)
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
        return maybe_convert_keys(data, self.opts.dump_key_fn)

    def handle_error(self, error, data, **kwargs):
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

        # validate id
        model_pk = self.Meta.model.Meta.pk
        if model_pk in self.fields:
            self.fields[model_pk].validators.append(self.validate_id)

        read_only_fields = {
            'slug',
            self.Meta.model.Meta.created_at,
            self.Meta.model.Meta.updated_at,
        }
        for name in read_only_fields:
            if name in self.fields:
                field = self.fields[name]
                field.dump_only = True
                self.dump_fields[name] = field
                self.load_fields.pop(name, None)

    def validate_id(self, id):
        if self.is_create() or (self.instance and int(id) == int(self.instance.id)):
            return
        raise MarshmallowValidationError('ids do not match')


__all__ = [
    'ModelSerializer',
]
