import sys

from flask_unchained import AppFactoryHook, FlaskUnchained
from flask_unchained.constants import TEST
from typing import *

from ..base_model import BaseModel
from ..model_registry import UnchainedModelRegistry


class RegisterModelsHook(AppFactoryHook):
    """
    Discovers SQLAlchemy models.
    """

    name = 'models'
    """
    The name of this hook.
    """

    bundle_module_names = ['models']
    """
    The default module this hook loads from.

    Override by setting the ``models_module_names`` attribute on your
    bundle class.
    """

    run_after = ['register_extensions']
    run_before = ['configure_app', 'init_extensions', 'services']

    def process_objects(self, app: FlaskUnchained, objects: Dict[str, Any]) -> None:
        """
        Finalize SQLAlchemy model mappings from the registry.
        """
        # this hook is responsible for discovering models, which happens by
        # importing each bundle's models module. the metaclasses of models
        # register themselves with the model registry, and the model registry
        # has final say over which models should end up getting mapped with
        # SQLAlchemy
        self.bundle.models = UnchainedModelRegistry().finalize_mappings()
        self.unchained._models_initialized = True

    def type_check(self, obj: Any) -> bool:
        """
        Returns True if ``obj`` is a concrete subclass of
        :class:`~flask_unchained.bundles.sqlalchemy.BaseModel`.
        """
        is_model = isinstance(obj, type) and issubclass(obj, BaseModel)
        return is_model and not obj.Meta.abstract

    def update_shell_context(self, ctx: dict):
        """
        Add models to the CLI shell context.
        """
        ctx.update(self.bundle.models)

    def import_bundle_modules(self, bundle):
        if self.unchained.env == TEST:
            for module_name in self.get_module_names(bundle):
                if module_name in sys.modules:
                    del sys.modules[module_name]
        return super().import_bundle_modules(bundle)
