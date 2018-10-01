import inspect
import sys

from flask_unchained import AppFactoryHook, FlaskUnchained
from flask_unchained.constants import TEST
from sqlalchemy_unchained import BaseModel as Model
from typing import *

from flask_unchained.bundles.sqlalchemy.model_registry import ModelRegistry


class RegisterModelsHook(AppFactoryHook):
    """
    Discovers models.
    """

    bundle_module_name = 'models'
    name = 'models'
    run_after = ['extensions']
    run_before = ['services', 'init_extensions']

    def process_objects(self, app: FlaskUnchained, _):
        # this hook is responsible for discovering models, which happens by
        # importing each bundle's models module. the metaclasses of models
        # register themselves with the model registry, and the model registry
        # has final say over which models should end up getting mapped with
        # SQLAlchemy
        self.bundle.models = ModelRegistry().finalize_mappings()

    def type_check(self, obj: Any) -> bool:
        if not inspect.isclass(obj) or not issubclass(obj, Model):
            return False
        return hasattr(obj, 'Meta') and not obj.Meta.abstract

    def update_shell_context(self, ctx: dict):
        ctx.update(self.bundle.models)

    def import_bundle_module(self, bundle):
        module_name = self.get_module_name(bundle)
        if self.unchained.env == TEST and module_name in sys.modules:
            del sys.modules[module_name]
        return super().import_bundle_module(bundle)
