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
    """
    The name of this hook.
    """

    bundle_module_names = ['services', 'managers']
    """
    The default modules this hook loads from.

    Override by setting the ``services_module_names`` attribute on your
    bundle class.
    """

    run_after = ['init_extensions']

    # skipcq: PYL-W0221 (parameters mismatch in overridden method)
    def process_objects(self,
                        app: FlaskUnchained,
                        services: Dict[str, Service],
                        ) -> None:
        """
        Register services with the Unchained extension, initialize them, and
        inject any requested into extensions.
        """
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
        """
        Returns the service's dependency injection name.
        """
        return obj.__di_name__

    def type_check(self, obj) -> bool:
        """
        Returns True if ``obj`` is a concrete subclass of
        :class:`~flask_unchained.Service`.
        """
        if not isinstance(obj, type):
            return False
        return issubclass(obj, Service) and hasattr(obj, '__di_name__')

    def update_shell_context(self, ctx: Dict[str, Any]) -> None:
        """
        Add services to the CLI shell context.
        """
        ctx.update(self.unchained.services)
