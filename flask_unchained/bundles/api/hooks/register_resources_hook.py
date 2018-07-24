import inspect

from flask_unchained import AppFactoryHook

from ..model_resource import ModelResource


class RegisterResourcesHook(AppFactoryHook):
    bundle_module_name = 'views'
    bundle_override_module_name_attr = 'resources_module_name'
    name = 'resources'
    run_after = ['models', 'serializers']

    def process_objects(self, app, objects):
        for name, resource_cls in objects.items():
            if isinstance(resource_cls.model, str):
                resource_cls.model = (self.unchained.sqlalchemy_bundle
                                      .models[resource_cls.model])
            model_name = resource_cls.model.__name__

            self.attach_serializers_to_resource_cls(model_name, resource_cls)
            self.store.resources_by_model[model_name] = resource_cls

    def attach_serializers_to_resource_cls(self, model_name, resource_cls):
        try:
            serializer_cls = self.store.serializers_by_model[model_name]
        except KeyError:
            raise KeyError(f'No serializer found for the {model_name} model')

        if resource_cls.serializer is None:
            resource_cls.serializer = serializer_cls()
        if resource_cls.serializer_many is None:
            resource_cls.serializer_many = self.store.many_by_model.get(
                model_name, serializer_cls)(many=True)
        if resource_cls.serializer_create is None:
            serializer = self.store.create_by_model.get(
                model_name, serializer_cls)()
            serializer.context['is_create'] = True
            resource_cls.serializer_create = serializer

    def type_check(self, obj):
        if not inspect.isclass(obj):
            return False
        return issubclass(obj, ModelResource) and obj != ModelResource
