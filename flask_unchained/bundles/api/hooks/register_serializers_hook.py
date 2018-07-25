import inspect

from flask import Flask
from flask_unchained import AppFactoryHook
from flask_unchained.string_utils import title_case

try:
    from marshmallow import class_registry
except ImportError:
    from flask_unchained import OptionalClass as class_registry

from ..model_serializer import ModelSerializer
from ..extensions import api


class RegisterSerializersHook(AppFactoryHook):
    bundle_module_name = 'serializers'
    name = 'serializers'
    run_after = ['models']

    def process_objects(self, app: Flask, objects):
        for name, serializer in objects.items():
            self.store.serializers[name] = serializer
            class_registry.register(name, serializer)

            model = serializer.Meta.model
            model_name = model if isinstance(model, str) else model.__name__
            kind = getattr(serializer, '__kind__', 'all')
            if kind == 'all':
                self.store.serializers_by_model[model_name] = serializer
                api.register_serializer(serializer, name=title_case(model_name))
            elif kind == 'create':
                self.store.create_by_model[model_name] = serializer
            elif kind == 'many':
                self.store.many_by_model[model_name] = serializer

    def type_check(self, obj):
        if not inspect.isclass(obj):
            return False
        return issubclass(obj, ModelSerializer) and obj != ModelSerializer

    def update_shell_context(self, ctx: dict):
        ctx.update(self.store.serializers)
