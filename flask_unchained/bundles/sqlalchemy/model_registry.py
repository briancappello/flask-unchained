import sys
import warnings

from py_meta_utils import McsInitArgs
from sqlalchemy.exc import SAWarning
from sqlalchemy_unchained import _ModelRegistry
from typing import *


class UnchainedModelRegistry(_ModelRegistry):
    enable_lazy_mapping = True

    def __init__(self):
        super().__init__()

        # like self._models, except its values are the relationships each model
        # class name expects on the other side
        # - keyed by model class name
        # - values are a dict:
        #   - keyed by the model name on the other side
        #   - value is the attribute expected to exist
        self._relationships: Dict[str, Dict[str, str]] = {}

    def _reset(self):
        for model in self._registry:
            for model_module in self._registry[model]:
                try:
                    del sys.modules[model_module]
                except KeyError:
                    pass

        super()._reset()
        self._relationships = {}

    def register(self, mcs_init_args: McsInitArgs):
        super().register(mcs_init_args)

        relationships = mcs_init_args.cls.Meta.relationships
        if relationships:
            self._relationships[mcs_init_args.name] = relationships

    def should_initialize(self, model_name):
        if model_name in self._initialized:
            return False

        if model_name not in self._relationships:
            return True

        with warnings.catch_warnings():
            # not all related classes will have been initialized yet, ie they
            # might still be non-mapped from SQLAlchemy's perspective, which is
            # safe to ignore here
            filter_re = r'Unmanaged access of declarative attribute \w+ from ' \
                        r'non-mapped class \w+'
            warnings.filterwarnings('ignore', filter_re, SAWarning)

            for related_model_name in self._relationships[model_name]:
                related_model = self._models[related_model_name].cls

                try:
                    other_side_relationships = \
                        self._relationships[related_model_name]
                except KeyError:
                    related_model_module = \
                        self._models[related_model_name].cls.__module__
                    raise KeyError(
                        'Incomplete `relationships` Meta declaration for '
                        f'{related_model_module}.{related_model_name} '
                        f'(missing {model_name})')

                if model_name not in other_side_relationships:
                    continue
                related_attr = other_side_relationships[model_name]
                if hasattr(related_model, related_attr):
                    return True


_ModelRegistry.set_singleton_class(UnchainedModelRegistry)
