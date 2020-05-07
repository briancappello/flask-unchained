from flask_unchained import Service, unchained
from flask_unchained.di import ServiceMetaclass, ServiceMetaOptionsFactory
from sqlalchemy_unchained.model_manager import (ModelManager as BaseModelManager,
                                                ModelManagerMetaclass as BaseModelManagerMetaclass)

from ..meta_options import ModelMetaOption


class ModelManagerMetaOptionsFactory(ServiceMetaOptionsFactory):
    _allowed_properties = ['model']
    _options = ServiceMetaOptionsFactory._options + [ModelMetaOption]

    def __init__(self):
        super().__init__()
        self._model = None

    @property
    def model(self):
        # make sure to always return the correct mapped model class
        if not unchained._models_initialized or not self._model:
            return self._model
        return unchained.sqlalchemy_bundle.models[self._model.__name__]

    @model.setter
    def model(self, model):
        self._model = model


class ModelManagerMetaclass(ServiceMetaclass, BaseModelManagerMetaclass):
    pass


class ModelManager(BaseModelManager, Service, metaclass=ModelManagerMetaclass):
    """
    Base class for database model manager services.
    """
    _meta_options_factory_class = ModelManagerMetaOptionsFactory

    class Meta:
        abstract = True
        model = None


__all__ = [
    'ModelManager',
    'ModelManagerMetaclass',
    'ModelManagerMetaOptionsFactory',
]
