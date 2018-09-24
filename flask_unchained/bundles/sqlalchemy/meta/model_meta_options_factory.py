import os
from flask_unchained.constants import TEST
from py_meta_utils import (
    AbstractMetaOption, MetaOption, MetaOptionsFactory, deep_getattr)
from typing import *

from .model_meta_options import (
    _TestingMetaOption,
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
    TableMetaOption,
    MaterializedViewForMetaOption,
)


class ModelMetaOptionsFactory(MetaOptionsFactory):
    def _get_meta_options(self) -> List[MetaOption]:
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
                   for option in self._get_meta_options()})
