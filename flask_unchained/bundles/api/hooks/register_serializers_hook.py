from flask import Flask
from flask_unchained import AppFactoryHook
from flask_unchained.string_utils import title_case

try:
    from marshmallow import class_registry
except ImportError:
    from py_meta_utils import OptionalClass as class_registry

from ..model_serializer import ModelSerializer
from ..extensions import api


class RegisterSerializersHook(AppFactoryHook):
    """
    Registers serializers.
    """

    bundle_module_name = 'serializers'
    name = 'serializers'
    run_after = ['models']

    def process_objects(self, app: Flask, objects):
        for name, serializer in objects.items():
            self.bundle.serializers[name] = serializer
            class_registry.register(name, serializer)

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

    def type_check(self, obj):
        if not isinstance(obj, type):
            return False
        return issubclass(obj, ModelSerializer) and obj != ModelSerializer

    def update_shell_context(self, ctx: dict):
        ctx.update(self.bundle.serializers)
