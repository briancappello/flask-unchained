import inspect

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

    # skipcq: PYL-W0221 (parameters mismatch in overridden method)
    def process_objects(self,
                        app: FlaskUnchained,
                        services: Dict[str, Service],
                        ) -> None:
        # register and initialize services
        for name, obj in services.items():
            self.unchained.register_service(name, obj)
        self.unchained._init_services()

        # inject services into extensions
        for ext in app.unchained.extensions.values():
            if not hasattr(ext, 'inject_services'):
                continue

            services = inspect.signature(ext.inject_services).parameters
            ext.inject_services(**{name: app.unchained.services.get(name)
                                   for name in services})

    def key_name(self, name, obj) -> str:
        return obj.__di_name__

    def type_check(self, obj) -> bool:
        if not isinstance(obj, type):
            return False
        return issubclass(obj, Service) and hasattr(obj, '__di_name__')

    def update_shell_context(self, ctx: Dict[str, Any]) -> None:
        ctx.update(self.unchained.services)
