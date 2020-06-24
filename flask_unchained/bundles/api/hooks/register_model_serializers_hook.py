from typing import *

from flask_unchained import AppFactoryHook, FlaskUnchained
from flask_unchained.string_utils import title_case

from ..model_serializer import ModelSerializer
from ..extensions import api


class RegisterModelSerializersHook(AppFactoryHook):
    """
    Registers ModelSerializers.
    """

    name = 'model_serializers'
    """
    The name of this hook.
    """

    bundle_module_names = ['serializers']
    """
    The default module this hook loads from.

    Override by setting the ``model_serializers_module_names`` attribute on your
    bundle class.
    """

    bundle_override_module_names_attr = 'model_serializers_module_names'

    run_after = ['models']

    # skipcq: PYL-W0221 (parameters mismatch in overridden method)
    def process_objects(self,
                        app: FlaskUnchained,
                        serializers: Dict[str, Type[ModelSerializer]],
                        ) -> None:
        """
        Registers model serializers onto the API Bundle instance.
        """
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
        """
        Returns True if ``obj`` is a subclass of
        :class:`~flask_unchained.bundles.api.ModelSerializer`.
        """
        if not isinstance(obj, type):
            return False
        return issubclass(obj, ModelSerializer) and obj != ModelSerializer

    def update_shell_context(self, ctx: Dict[str, Any]) -> None:
        """
        Adds model serializers to the CLI shell context.
        """
        ctx.update(self.bundle.serializers)
