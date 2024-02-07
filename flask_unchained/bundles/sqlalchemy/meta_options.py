from flask_unchained import unchained
from py_meta_utils import McsArgs, MetaOption
from sqlalchemy_unchained import ModelMetaOptionsFactory as BaseModelMetaOptionsFactory
from typing import *


class ModelMetaOption(MetaOption):
    """
    The model class for a class.
    """

    def __init__(self):
        super().__init__("model", default=None, inherit=True)

    def get_value(self, Meta: Type[object], base_classes_meta, mcs_args: McsArgs):
        value = super().get_value(Meta, base_classes_meta, mcs_args)
        if value and unchained._models_initialized:
            value = unchained.sqlalchemy_bundle.models.get(value.__name__, value)
        return value

    def check_value(self, value, mcs_args: McsArgs):
        if mcs_args.Meta.abstract:
            return

        from .base_model import BaseModel

        if not (isinstance(value, type) and issubclass(value, BaseModel)):
            raise TypeError(f"{mcs_args.name} is missing the model Meta attribute")
