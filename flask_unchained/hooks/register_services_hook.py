import inspect

from ..app_factory_hook import AppFactoryHook
from ..di import BaseService


class RegisterServicesHook(AppFactoryHook):
    """
    Registers services for dependency injection
    """
    bundle_module_name = 'services'
    name = 'services'
    run_after = ['init_extensions']

    def process_objects(self, app, services):
        for name, obj in services.items():
            self.unchained.register_service(name, obj)
        self.unchained._init_services()

    def key_name(self, name, obj):
        return obj.__di_name__

    def type_check(self, obj):
        if not inspect.isclass(obj):
            return False
        return issubclass(obj, BaseService) and hasattr(obj, '__di_name__')

    def update_shell_context(self, ctx: dict):
        ctx.update(self.unchained.services)
