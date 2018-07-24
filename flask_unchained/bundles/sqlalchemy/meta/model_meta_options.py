from flask_unchained.string_utils import snake_case
from sqlalchemy import func as sa_func, types as sa_types
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import RelationshipProperty

from ..sqla.column import Column
from ..sqla.relationships import foreign_key
from ..sqla.types import BigInteger, DateTime

from .types import McsArgs

_default = type('_default', (), {'__bool__': lambda x: False})()


class MetaOption:
    def __init__(self, name, default=None, inherit=False):
        self.name = name
        self.default = default
        self.inherit = inherit

    def get_value(self, meta, base_model_meta, mcs_args: McsArgs):
        """
        :param meta: the class Meta (if any) from the user's model (NOTE:
            this will be a plain object, NOT an instance of ModelMetaOptions)
        :param base_model_meta: the ModelMetaOptions (if any) from the
            base class of the user's model
        :param mcs_args: the McsArgs for the user's model class
        """
        value = self.default
        if self.inherit and base_model_meta is not None:
            value = getattr(base_model_meta, self.name, value)
        if meta is not None:
            value = getattr(meta, self.name, value)
        return value

    def check_value(self, value, mcs_args: McsArgs):
        pass

    def contribute_to_class(self, mcs_args: McsArgs, value):
        pass

    def __repr__(self):
        return f'<{self.__class__.__name__} name={self.name!r}, ' \
               f'default={self.default!r}, inherit={self.inherit}>'


class ColumnMetaOption(MetaOption):
    def get_value(self, meta, base_model_meta, mcs_args: McsArgs):
        value = super().get_value(meta, base_model_meta, mcs_args)
        return self.default if value is True else value

    def check_value(self, value, mcs_args: McsArgs):
        msg = f'{self.name} Meta option on {mcs_args.model_repr} ' \
              f'must be a str, bool or None'
        assert value is None or isinstance(value, (bool, str)), msg

    def contribute_to_class(self, mcs_args: McsArgs, col_name):
        is_polymorphic = mcs_args.model_meta.polymorphic
        is_polymorphic_base = mcs_args.model_meta._is_base_polymorphic_model

        if (mcs_args.model_meta.abstract
                or (is_polymorphic and not is_polymorphic_base)):
            return

        if col_name and col_name not in mcs_args.clsdict:
            mcs_args.clsdict[col_name] = self.get_column(mcs_args)

    def get_column(self, mcs_args: McsArgs):
        raise NotImplementedError


class AbstractMetaOption(MetaOption):
    def __init__(self):
        super().__init__(name='abstract', default=False, inherit=False)

    def get_value(self, meta, base_model_meta, mcs_args: McsArgs):
        if '__abstract__' in mcs_args.clsdict:
            return True
        return super().get_value(meta, base_model_meta, mcs_args)

    def contribute_to_class(self, mcs_args: McsArgs, is_abstract):
        if is_abstract:
            mcs_args.clsdict['__abstract__'] = True


class PrimaryKeyColumnMetaOption(ColumnMetaOption):
    def __init__(self, name='pk', default='id', inherit=True):
        super().__init__(name=name, default=default, inherit=inherit)

    def get_column(self, mcs_args: McsArgs):
        return Column(BigInteger, primary_key=True)


class CreatedAtColumnMetaOption(ColumnMetaOption):
    def __init__(self, name='created_at', default='created_at', inherit=True):
        super().__init__(name=name, default=default, inherit=inherit)

    def get_column(self, mcs_args: McsArgs):
        return Column(DateTime, server_default=sa_func.now())


class UpdatedAtColumnMetaOption(ColumnMetaOption):
    def __init__(self, name='updated_at', default='updated_at', inherit=True):
        super().__init__(name=name, default=default, inherit=inherit)

    def get_column(self, mcs_args: McsArgs):
        return Column(DateTime,
                      server_default=sa_func.now(), onupdate=sa_func.now())


class LazyMappedMetaOption(MetaOption):
    def __init__(self, name='lazy_mapped', default=False, inherit=True):
        super().__init__(name=name, default=default, inherit=inherit)


class RelationshipsMetaOption(MetaOption):
    def __init__(self):
        super().__init__('relationships', inherit=True)

    def get_value(self, meta, base_model_meta, mcs_args: McsArgs):
        """overridden to merge with inherited value"""
        if mcs_args.model_meta.abstract:
            return None
        value = getattr(base_model_meta, self.name, {}) or {}
        value.update(getattr(meta, self.name, {}))
        return value

    def contribute_to_class(self, mcs_args: McsArgs, relationships):
        if mcs_args.model_meta.abstract:
            return

        discovered_relationships = {}

        def discover_relationships(d):
            for k, v in d.items():
                if isinstance(v, RelationshipProperty):
                    discovered_relationships[v.argument] = k
                    if v.backref and mcs_args.model_meta.lazy_mapped:
                        raise Exception(
                            f'Discovered a lazy-mapped backref `{k}` on '
                            f'`{mcs_args.model_repr}`. Currently this '
                            'is unsupported; please use `db.relationship` with '
                            'the `back_populates` kwarg on both sides instead.')

        for base in mcs_args.bases:
            discover_relationships(vars(base))
        discover_relationships(mcs_args.clsdict)

        relationships.update(discovered_relationships)


class _TestingMetaOption(MetaOption):
    def __init__(self):
        super().__init__('_testing_', default=None, inherit=True)


class PolymorphicBaseTablenameMetaOption(MetaOption):
    def __init__(self):
        super().__init__('_base_tablename', default=None, inherit=False)

    def get_value(self, meta, base_model_meta, mcs_args: McsArgs):
        if base_model_meta and not base_model_meta.abstract:
            bm = base_model_meta._mcs_args
            clsdicts = [bm.clsdict] + [b._meta._mcs_args.clsdict
                                       for b in bm.bases
                                       if hasattr(b, '_meta')]
            declared_attrs = [isinstance(d.get('__tablename__'), declared_attr)
                              for d in clsdicts]
            if any(declared_attrs):
                return None
            return bm.clsdict.get('__tablename__', snake_case(bm.name))


class PolymorphicOnColumnMetaOption(ColumnMetaOption):
    def __init__(self, name='polymorphic_on', default='discriminator'):
        super().__init__(name=name, default=default)

    def get_value(self, meta, base_model_meta, mcs_args: McsArgs):
        if mcs_args.model_meta.polymorphic not in {'single', 'joined'}:
            return None
        return super().get_value(meta, base_model_meta, mcs_args)

    def contribute_to_class(self, mcs_args: McsArgs, col_name):
        if mcs_args.model_meta.polymorphic not in {'single', 'joined'}:
            return

        # maybe add the polymorphic_on discriminator column
        super().contribute_to_class(mcs_args, col_name)

        mapper_args = mcs_args.clsdict.get('__mapper_args__', {})
        if (mcs_args.model_meta._is_base_polymorphic_model
                and 'polymorphic_on' not in mapper_args):
            mapper_args['polymorphic_on'] = mcs_args.clsdict[col_name]
            mcs_args.clsdict['__mapper_args__'] = mapper_args

    def get_column(self, model_meta_options):
        return Column(sa_types.String)


class PolymorphicJoinedPkColumnMetaOption(ColumnMetaOption):
    def __init__(self):
        # name, default, and inherited are all ignored for this option
        super().__init__(name='_', default='_')

    def contribute_to_class(self, mcs_args: McsArgs, value):
        model_meta = mcs_args.model_meta
        if model_meta.abstract or not model_meta._base_tablename:
            return

        pk = model_meta.pk or 'id'  # FIXME is this default a good idea?
        if (model_meta.polymorphic == 'joined'
                and not model_meta._is_base_polymorphic_model
                and pk not in mcs_args.clsdict):
            mcs_args.clsdict[pk] = self.get_column(mcs_args)

    def get_column(self, mcs_args: McsArgs):
        return foreign_key(mcs_args.model_meta._base_tablename,
                           primary_key=True, fk_col=mcs_args.model_meta.pk)


class PolymorphicTableArgsMetaOption(MetaOption):
    def __init__(self):
        # name, default, and inherited are all ignored for this option
        super().__init__(name='_', default='_')

    def contribute_to_class(self, mcs_args: McsArgs, value):
        if (mcs_args.model_meta.polymorphic == 'single'
                and mcs_args.model_meta._is_base_polymorphic_model):
            mcs_args.clsdict['__table_args__'] = None


class PolymorphicIdentityMetaOption(MetaOption):
    def __init__(self, name='polymorphic_identity', default=None):
        super().__init__(name=name, default=default, inherit=False)

    def get_value(self, meta, base_model_meta, mcs_args: McsArgs):
        if mcs_args.model_meta.polymorphic in {False, '_fully_manual_'}:
            return None

        identifier = super().get_value(meta, base_model_meta, mcs_args)
        mapper_args = mcs_args.clsdict.get('__mapper_args__', {})
        return mapper_args.get('polymorphic_identity',
                               identifier or mcs_args.name)

    def contribute_to_class(self, mcs_args: McsArgs, identifier):
        if mcs_args.model_meta.polymorphic in {False, '_fully_manual_'}:
            return

        mapper_args = mcs_args.clsdict.get('__mapper_args__', {})
        if 'polymorphic_identity' not in mapper_args:
            mapper_args['polymorphic_identity'] = identifier
            mcs_args.clsdict['__mapper_args__'] = mapper_args


class PolymorphicMetaOption(MetaOption):
    def __init__(self):
        super().__init__('polymorphic', default=False, inherit=True)

    def get_value(self, meta, base_model_meta, mcs_args: McsArgs):
        mapper_args = mcs_args.clsdict.get('__mapper_args__', {})
        if isinstance(mapper_args, declared_attr):
            return '_fully_manual_'
        elif 'polymorphic_on' in mapper_args:
            return '_manual_'

        value = super().get_value(meta, base_model_meta, mcs_args)
        return 'joined' if value is True else value

    def check_value(self, value, mcs_args: McsArgs):
        if value in {'_manual_', '_fully_manual_'}:
            return

        valid = ['joined', 'single', True, False]
        msg = '{name} Meta option on {model} must be one of {choices}'.format(
            name=self.name,
            model=mcs_args.model_repr,
            choices=', '.join(f'{c!r}' for c in valid))
        assert value in valid, msg


class TableMetaOption(MetaOption):
    def __init__(self):
        super().__init__(name='table', default=_default, inherit=False)

    def get_value(self, meta, base_model_meta, mcs_args: McsArgs):
        manual = mcs_args.clsdict.get('__tablename__')
        if isinstance(manual, declared_attr):
            return None
        elif manual:
            return manual

        value = super().get_value(meta, base_model_meta, mcs_args)
        if value:
            return value
        elif 'selectable' in mcs_args.clsdict:  # db.MaterializedView
            return snake_case(mcs_args.name)

    def contribute_to_class(self, mcs_args: McsArgs, value):
        if value:
            mcs_args.clsdict['__tablename__'] = value


class MaterializedViewForMetaOption(MetaOption):
    def __init__(self):
        super().__init__(name='mv_for', default=None, inherit=True)

    def get_value(self, meta, base_model_meta, mcs_args: McsArgs):
        return super().get_value(meta, base_model_meta, mcs_args) or []
