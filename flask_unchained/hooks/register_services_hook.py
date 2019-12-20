from typing import *

from ..app_factory_hook import AppFactoryHook
from ..di import Service
from ..flask_unchained import FlaskUnchained


class RegisterServicesHook(AppFactoryHook):
    """
    Registers services for dependency injection.
    """

    name = 'services'
    bundle_module_names = ['services']
    run_after = ['init_extensions']

    def process_objects(self,
                        app: FlaskUnchained,
                        services: Dict[str, Service],
                        ) -> None:
        for name, obj in services.items():
            self.unchained.register_service(name, obj)
        self.unchained._init_services()

    def key_name(self, name, obj) -> str:
        return obj.__di_name__

    def type_check(self, obj) -> bool:
        if not isinstance(obj, type):
            return False
        return issubclass(obj, Service) and hasattr(obj, '__di_name__')

    def update_shell_context(self, ctx: Dict[str, Any]) -> None:
        ctx.update(self.unchained.services)
