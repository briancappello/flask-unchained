import inspect
import sys

from flask_unchained import AppFactoryHook, FlaskUnchained, unchained, injectable
from flask_unchained.constants import TEST
from typing import *

from ..extensions import SQLAlchemyUnchained
from ..forms import ModelForm, model_fields, _ModelConverter
from ..model_registry import UnchainedModelRegistry


class RegisterModelsAndModelFormsHook(AppFactoryHook):
    """
    Discovers models and model forms.
    """

    name = 'models'
    bundle_module_names = ['models', 'forms']
    run_after = ['register_extensions']
    run_before = ['configure_app', 'init_extensions', 'services']

    @unchained.inject('db')
    def process_objects(self,
                        app: FlaskUnchained,
                        model_forms: Dict[str, Type[ModelForm]],
                        db: SQLAlchemyUnchained = injectable,
                        ) -> None:
        # this hook is responsible for discovering models, which happens by
        # importing each bundle's models module. the metaclasses of models
        # register themselves with the model registry, and the model registry
        # has final say over which models should end up getting mapped with
        # SQLAlchemy
        self.bundle.models = UnchainedModelRegistry().finalize_mappings()
        self.unchained._models_initialized = True

        # this hook is also responsible for making sure ModelForm subclasses have
        # the correct fields. We can only figure that out after the mappings have
        # been finalized. So this is hacky/magical fix to get it working as best as
        # possible (or rather, as best I could figure out).

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # WARNING: if any module in user code imports any of these form classes before
        # this hook has a chance to monkeypatch it, EVERYTHING BREAKS. The errors will
        # be opaque, saying YourFormClass.a_field_name_from_the_model does not exist.
        for name, form_cls in model_forms.items():
            if not getattr(form_cls.Meta, 'model', None):
                continue
            form_cls.Meta.model = self.bundle.models[form_cls.Meta.model.__name__]
            new_fields = model_fields(form_cls.Meta.model,
                                      only=form_cls.Meta.only,
                                      exclude=form_cls.Meta.exclude,
                                      exclude_fk=form_cls.Meta.exclude_fk,
                                      exclude_pk=form_cls.Meta.exclude_pk,
                                      field_args=form_cls.Meta.field_args,
                                      db_session=db.session,
                                      converter=_ModelConverter())
            new_form_cls = type(name, (ModelForm,), dict(
                **new_fields,
                **form_cls.__dict__.copy(),  # user-declared fields override the defaults
            ))
            setattr(inspect.getmodule(form_cls), name, new_form_cls)

    def type_check(self, obj: Any) -> bool:
        is_form_subclass = isinstance(obj, type) and issubclass(obj, ModelForm)
        return is_form_subclass and hasattr(obj, 'Meta') and not obj.Meta.abstract

    def update_shell_context(self, ctx: dict):
        ctx.update(self.bundle.models)

    def import_bundle_modules(self, bundle):
        if self.unchained.env == TEST:
            for module_name in self.get_module_names(bundle):
                if module_name in sys.modules:
                    del sys.modules[module_name]
        return super().import_bundle_modules(bundle)
