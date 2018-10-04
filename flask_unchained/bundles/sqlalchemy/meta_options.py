import inspect

from py_meta_utils import McsArgs, MetaOption
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy_unchained import ModelMetaOptionsFactory as BaseMetaOptionsFactory
from typing import *


class ModelMetaOption(MetaOption):
    """
    The model class this model resource is for.
    """
    def __init__(self):
        super().__init__('model', default=None, inherit=True)

    def check_value(self, value, mcs_args: McsArgs):
        if mcs_args.Meta.abstract:
            return

        from .base_model import BaseModel
        assert inspect.isclass(value) and issubclass(value, BaseModel), \
            f'{mcs_args.name} is missing the model Meta attribute'


class RelationshipsMetaOption(MetaOption):
    def __init__(self):
        super().__init__('relationships', inherit=True)

    def get_value(self, meta, base_model_meta, mcs_args: McsArgs):
        """overridden to merge with inherited value"""
        if mcs_args.Meta.abstract:
            return None
        value = getattr(base_model_meta, self.name, {}) or {}
        value.update(getattr(meta, self.name, {}))
        return value

    def contribute_to_class(self, mcs_args: McsArgs, relationships):
        if mcs_args.Meta.abstract:
            return

        discovered_relationships = {}

        def discover_relationships(d):
            for k, v in d.items():
                if isinstance(v, RelationshipProperty):
                    discovered_relationships[v.argument] = k
                    if v.backref and mcs_args.Meta.lazy_mapped:
                        raise NotImplementedError(
                            f'Discovered a lazy-mapped backref `{k}` on '
                            f'`{mcs_args.repr}`. Currently this '
                            'is unsupported; please use `db.relationship` with '
                            'the `back_populates` kwarg on both sides instead.')

        for base in mcs_args.bases:
            discover_relationships(vars(base))
        discover_relationships(mcs_args.clsdict)

        relationships.update(discovered_relationships)


class MaterializedViewForMetaOption(MetaOption):
    def __init__(self):
        super().__init__(name='mv_for', default=None, inherit=True)

    def get_value(self, meta, base_model_meta, mcs_args: McsArgs):
        return super().get_value(meta, base_model_meta, mcs_args) or []


class ModelMetaOptionsFactory(BaseMetaOptionsFactory):
    def _get_meta_options(self) -> List[MetaOption]:
        """"
        Define fields allowed in the Meta class on end-user models, and the
        behavior of each.

        Custom ModelMetaOptions classes should override this method to customize
        the options supported on class Meta of end-user models.
        """
        return super()._get_meta_options() + [RelationshipsMetaOption(),
                                              MaterializedViewForMetaOption()]
