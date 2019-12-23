from typing import *

from flask_unchained import AppFactoryHook, FlaskUnchained
from flask_unchained.string_utils import title_case

from ..model_serializer import ModelSerializer
from ..extensions import api


class RegisterSerializersHook(AppFactoryHook):
    """
    Registers serializers.
    """

    name = 'serializers'
    bundle_module_names = ['serializers']
    run_after = ['models']

    # skipcq: PYL-W0221 (parameters mismatch in overridden method)
    def process_objects(self,
                        app: FlaskUnchained,
                        serializers: Dict[str, Type[ModelSerializer]],
                        ) -> None:
        for name, serializer in serializers.items():
            self.bundle.serializers[name] = serializer

            model = serializer.Meta.model
            model_name = model if isinstance(model, str) else model.__name__

            kind = getattr(serializer, '__kind__', 'all')
            if kind == 'all':
                self.bundle.serializers_by_model[model_name] = serializer
                api.register_serializer(serializer, name=title_case(model_name))
            elif kind == 'create':
                self.bundle.create_by_model[model_name] = serializer
            elif kind == 'many':
                self.bundle.many_by_model[model_name] = serializer

    def type_check(self, obj: Any) -> bool:
        if not isinstance(obj, type):
            return False
        return issubclass(obj, ModelSerializer) and obj != ModelSerializer

    def update_shell_context(self, ctx: Dict[str, Any]) -> None:
        ctx.update(self.bundle.serializers)
