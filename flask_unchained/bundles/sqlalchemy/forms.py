from flask_unchained import FlaskForm, unchained
from py_meta_utils import (
    AbstractMetaOption, McsArgs, MetaOption, MetaOptionsFactory, _missing,
    process_factory_meta_options)
from sqlalchemy_unchained.validation import ValidationError, ValidationErrors
from typing import *
from wtforms.ext.sqlalchemy.fields import *
from wtforms.ext.sqlalchemy.orm import ModelConverter as _BaseModelConverter, converts
from wtforms.form import FormMeta as _FormMetaclass

from .extensions import db
from .meta_options import ModelMetaOption


class OnlyMetaOption(MetaOption):
    def __init__(self):
        super().__init__('only', default=None, inherit=True)

    def check_value(self, value: Any, mcs_args: McsArgs):
        if mcs_args.Meta.abstract or value is None:
            return

        if (not isinstance(value, (list, tuple))
                or not all([isinstance(x, str) for x in value])):
            raise TypeError(f'The `only` Meta option for {mcs_args.name} must be '
                            f'a list (or tuple) of strings')


class ExcludeMetaOption(MetaOption):
    def __init__(self):
        super().__init__('exclude', default=_missing, inherit=True)

    def get_value(self, Meta: Type[object], base_classes_meta, mcs_args: McsArgs):
        value = super().get_value(Meta, base_classes_meta, mcs_args)
        if not mcs_args.Meta.abstract and value is _missing:
            value = (mcs_args.Meta.model.Meta.created_at, mcs_args.Meta.model.Meta.updated_at)
        return value

    def check_value(self, value: Any, mcs_args: McsArgs):
        if mcs_args.Meta.abstract or value is None:
            return

        if (not isinstance(value, (list, tuple))
                or not all([isinstance(x, str) for x in value])):
            raise TypeError(f'The `exclude` Meta option for {mcs_args.name} must be '
                            f'a list (or tuple) of strings')


class FieldArgsMetaOption(MetaOption):
    def __init__(self):
        super().__init__('field_args', default=None, inherit=True)

    def check_value(self, value: Any, mcs_args: McsArgs):
        if mcs_args.Meta.abstract or value is None:
            return

        if not isinstance(value, dict):
            raise TypeError(f'The `field_args` Meta option for {mcs_args.name} '
                            f'must be a dictionary')


class ExcludePrimaryKeyMetaOption(MetaOption):
    def __init__(self):
        super().__init__('exclude_pk', default=True, inherit=True)

    def check_value(self, value: Any, mcs_args: McsArgs):
        if mcs_args.Meta.abstract:
            return

        if not isinstance(value, bool):
            raise TypeError(f'The `exclude_pk` Meta option for {mcs_args.name} '
                            f'must be a boolean')


class ExcludeForeignKeyMetaOption(MetaOption):
    def __init__(self):
        super().__init__('exclude_fk', default=True, inherit=True)

    def check_value(self, value: Any, mcs_args: McsArgs):
        if mcs_args.Meta.abstract:
            return

        if not isinstance(value, bool):
            raise TypeError(f'The `exclude_fk` Meta option for {mcs_args.name} '
                            f'must be a boolean')


class ModelFieldsMetaOption(MetaOption):
    def __init__(self):
        super().__init__('model_fields', default=None, inherit=True)

    def check_value(self, value: Any, mcs_args: McsArgs):
        if mcs_args.Meta.abstract or value is None:
            return

        if not isinstance(value, dict):
            raise TypeError(f'The `model_fields` Meta option for {mcs_args.name} '
                            f'must be a dictionary')


class ModelFormMetaOptionsFactory(MetaOptionsFactory):
    _options = [
        AbstractMetaOption,
        ModelMetaOption,
        OnlyMetaOption,
        ExcludeMetaOption,
        ExcludeForeignKeyMetaOption,
        ExcludePrimaryKeyMetaOption,
        FieldArgsMetaOption,
        ModelFieldsMetaOption,
    ]


class _ModelConverter(_BaseModelConverter):
    @converts('Integer', 'SmallInteger', 'BigInteger')
    def handle_integer_types(self, column, field_args, **extra):
        return super().handle_integer_types(column, field_args, **extra)


# this function is copied from wtforms.ext.sqlalchemy, aside from one line (marked)
def model_fields(model, db_session=None, only=None, exclude=None,
                 field_args=None, converter=None, exclude_pk=False,
                 exclude_fk=False):
    """
    Generate a dictionary of fields for a given SQLAlchemy model.

    See `model_form` docstring for description of parameters.
    """
    mapper = model._sa_class_manager.mapper
    converter = converter or _ModelConverter()
    field_args = field_args or {}
    properties = []

    for prop in mapper.iterate_properties:
        if getattr(prop, 'columns', None):
            if exclude_fk and prop.columns[0].foreign_keys:
                continue
            elif exclude_pk and prop.columns[0].primary_key:
                continue

        properties.append((prop.key, prop))

    # the following if condition is modified:
    if only is not None:
        properties = (x for x in properties if x[0] in only)
    elif exclude:
        properties = (x for x in properties if x[0] not in exclude)

    field_dict = {}
    for name, prop in properties:
        field = converter.convert(
            model, mapper, prop,
            field_args.get(name), db_session
        )
        if field is not None:
            field_dict[name] = field

    return field_dict


class _ModelFormMetaclass(_FormMetaclass):
    def __new__(mcs, name, bases, clsdict):
        mcs_args = McsArgs(mcs, name, bases, clsdict)
        Meta = process_factory_meta_options(mcs_args, ModelFormMetaOptionsFactory)
        mcs_args.clsdict['Meta'] = type('Meta', (), Meta._to_clsdict())
        if not Meta.abstract and unchained._models_initialized:
            try:
                Meta.model = unchained.sqlalchemy_bundle.models[Meta.model.__name__]
            except KeyError:
                pass
            new_clsdict = model_fields(Meta.model,
                                       only=Meta.only,
                                       exclude=Meta.exclude,
                                       exclude_fk=Meta.exclude_fk,
                                       exclude_pk=Meta.exclude_pk,
                                       field_args=Meta.field_args,
                                       db_session=db.session,
                                       converter=_ModelConverter())
            new_clsdict.update(mcs_args.clsdict)
            mcs_args.clsdict = new_clsdict
        return super().__new__(*mcs_args)


class ModelForm(FlaskForm, metaclass=_ModelFormMetaclass):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        try:
            model_name = self.Meta.model.__name__
            self.Meta.model = unchained.sqlalchemy_bundle.models[model_name]
        except KeyError:
            pass
        super().__init__(*args, **kwargs)

    def validate(self):
        validation_passed = super().validate()
        if not self.Meta.model:
            return validation_passed

        try:
            self.Meta.model.validate(**{k: v for k, v in self.data.items()
                                        if hasattr(self.Meta.model, k)})
        except ValidationErrors as e:
            for col_name, errors in e.errors.items():
                field = self._fields[col_name]
                for e in errors:
                    field.errors.append(e)

        if self.Meta.model_fields:
            for field_name, column_name in self.Meta.model_fields.items():
                field = self._fields[field_name]

                for v in self.Meta.model._get_validators(column_name):
                    try:
                        v(field.data)
                    except ValidationError as e:
                        e.model = self.Meta.model
                        e.column = column_name
                        field.errors.append(str(e))
                        validation_passed = False

        if not validation_passed:
            return validation_passed

        return len(self.errors) == 0

    @property
    def errors(self):
        if self._errors:
            return self._errors
        return dict((name, f.errors) for name, f in self._fields.items() if f.errors)

    @property
    def data(self):
        return dict((name, f.data) for name, f in self._fields.items())

    def make_instance(self):
        return self.Meta.model(**self.data)


__all__ = [
    'ModelForm',
]
