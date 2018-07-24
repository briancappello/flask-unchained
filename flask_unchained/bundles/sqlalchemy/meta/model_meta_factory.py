import os
from flask_unchained.constants import TEST
from flask_unchained.utils import deep_getattr
from typing import *

from .model_meta_options import (
    _TestingMetaOption,
    AbstractMetaOption,
    LazyMappedMetaOption,
    RelationshipsMetaOption,
    PolymorphicMetaOption,
    PolymorphicOnColumnMetaOption,
    PolymorphicIdentityMetaOption,
    PolymorphicBaseTablenameMetaOption,
    PolymorphicJoinedPkColumnMetaOption,
    PrimaryKeyColumnMetaOption,
    CreatedAtColumnMetaOption,
    UpdatedAtColumnMetaOption,
    MetaOption,
    TableMetaOption,
    MaterializedViewForMetaOption,
)
from .types import McsArgs


class ModelMetaFactory:
    def __init__(self):
        self._mcs_args: McsArgs = None

    def _get_model_meta_options(self) -> List[MetaOption]:
        """"
        Define fields allowed in the Meta class on end-user models, and the
        behavior of each.

        Custom ModelMetaOptions classes should override this method to customize
        the options supported on class Meta of end-user models.
        """
        # we can't use current_app to determine if we're under test, because it
        # doesn't exist yet
        testing_options = ([] if os.getenv('FLASK_ENV', False) != TEST
                           else [_TestingMetaOption()])

        # when options require another option, its dependent must be listed.
        # options in this list are not order-dependent, except where noted.
        # all ColumnMetaOptions subclasses require PolymorphicMetaOption
        return testing_options + [
            AbstractMetaOption(),  # required; must be first
            LazyMappedMetaOption(),
            RelationshipsMetaOption(),  # requires lazy_mapped
            TableMetaOption(),
            MaterializedViewForMetaOption(),

            PolymorphicMetaOption(),  # must be first of all polymorphic options
            PolymorphicOnColumnMetaOption(),
            PolymorphicIdentityMetaOption(),
            PolymorphicBaseTablenameMetaOption(),
            PolymorphicJoinedPkColumnMetaOption(),  # requires _BaseTablename

            # must be after PolymorphicJoinedPkColumnMetaOption
            PrimaryKeyColumnMetaOption(),
            CreatedAtColumnMetaOption(),
            UpdatedAtColumnMetaOption(),
        ]

    def _contribute_to_class(self, mcs_args: McsArgs):
        self._mcs_args = mcs_args

        meta = mcs_args.clsdict.pop('Meta', None)
        base_model_meta = deep_getattr(
            mcs_args.clsdict, mcs_args.bases, '_meta', None)

        mcs_args.clsdict['_meta'] = self

        options = self._get_model_meta_options()
        if (os.getenv('FLASK_ENV', None) != TEST
                and not isinstance(options[0], AbstractMetaOption)):
            raise Exception('The first option in _get_model_meta_options '
                            'must be an instance of AbstractMetaOption')

        self._fill_from_meta(meta, base_model_meta, mcs_args)
        for option in options:
            option_value = getattr(self, option.name, None)
            option.contribute_to_class(mcs_args, option_value)

    def _fill_from_meta(self, meta, base_model_meta, mcs_args: McsArgs):
        # Exclude private/protected fields from the meta
        meta_attrs = {} if not meta else {k: v for k, v in vars(meta).items()
                                          if not k.startswith('_')}

        for option in self._get_model_meta_options():
            assert not hasattr(self, option.name), \
                f"Can't override field {option.name}."
            value = option.get_value(meta, base_model_meta, mcs_args)
            option.check_value(value, mcs_args)
            meta_attrs.pop(option.name, None)
            if option.name != '_':
                setattr(self, option.name, value)

        if meta_attrs:
            # Some attributes in the Meta aren't allowed here
            raise TypeError(
                f"'class Meta' for {self._model_repr!r} got unknown "
                f"attribute(s) {','.join(sorted(meta_attrs.keys()))}")

    @property
    def _is_base_polymorphic_model(self):
        if not self.polymorphic:
            return False
        base_meta = deep_getattr({}, self._mcs_args.bases, '_meta')
        return base_meta.abstract

    @property
    def _model_repr(self):
        return self._mcs_args.model_repr

    def __repr__(self):
        return '<{cls} model={model!r} model_meta_options={attrs!r}>'.format(
            cls=self.__class__.__name__,
            model=self._model_repr,
            attrs={option.name: getattr(self, option.name, None)
                   for option in self._get_model_meta_options()})
