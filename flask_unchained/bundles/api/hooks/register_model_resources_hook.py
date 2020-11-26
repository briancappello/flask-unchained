from flask_unchained import AppFactoryHook
from flask_unchained.hooks.views_hook import ViewsHook

from ..model_resource import ModelResource


class RegisterModelResourcesHook(AppFactoryHook):
    """
    Registers ModelResources and configures ModelSerializers on them.
    """

    name = 'model_resources'
    """
    The name of this hook.
    """

    bundle_module_names = ViewsHook.bundle_module_names
    """
    The default module this hook loads from.

    Override by setting the ``model_resources_module_names`` attribute on your
    bundle class.
    """

    bundle_override_module_names_attr = 'model_resources_module_names'

    run_after = ['models', 'model_serializers']

    def process_objects(self, app, objects):
        """
        Configures ModelSerializers on ModelResources.
        """
        for resource_cls in objects.values():
            if isinstance(resource_cls.Meta.model, str):
                resource_cls.Meta.model = \
                    self.unchained.sqlalchemy_bundle.models[resource_cls.Meta.model]
            model_name = resource_cls.Meta.model.__name__

            self.attach_serializers_to_resource_cls(model_name, resource_cls)
            self.bundle.resources_by_model[model_name] = resource_cls

    def attach_serializers_to_resource_cls(self, model_name, resource_cls):
        try:
            serializer_cls = self.bundle.serializers_by_model[model_name]
        except KeyError as e:
            raise KeyError(f'No serializer found for the {model_name} model') from e

        if resource_cls.Meta.serializer is None:
            resource_cls.Meta.serializer = serializer_cls()
        elif isinstance(resource_cls.Meta.serializer, type):
            resource_cls.Meta.serializer = resource_cls.Meta.serializer()

        if resource_cls.Meta.serializer_many is None:
            resource_cls.Meta.serializer_many = self.bundle.many_by_model.get(
                model_name, serializer_cls)(many=True)
        elif isinstance(resource_cls.Meta.serializer_many, type):
            resource_cls.Meta.serializer_many = \
                resource_cls.Meta.serializer_many(many=True)

        if resource_cls.Meta.serializer_create is None:
            resource_cls.Meta.serializer_create = self.bundle.create_by_model.get(
                model_name, serializer_cls)(context=dict(is_create=True))
        elif isinstance(resource_cls.Meta.serializer_create, type):
            resource_cls.Meta.serializer_create = \
                resource_cls.Meta.serializer_create(context=dict(is_create=True))

    def type_check(self, obj):
        """
        Returns True if ``obj`` is a subclass of
        :class:`~flask_unchained.bundles.api.ModelResource`.
        """
        if not isinstance(obj, type):
            return False
        return issubclass(obj, ModelResource) and obj != ModelResource
