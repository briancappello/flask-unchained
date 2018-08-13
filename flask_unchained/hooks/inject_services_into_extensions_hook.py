import inspect

from typing import *

from ..app_factory_hook import AppFactoryHook
from ..bundle import Bundle
from ..flask_unchained import FlaskUnchained


class InjectServicesIntoExtensionsHook(AppFactoryHook):
    """
    Injects services into extensions.
    """

    bundle_module_name = None
    name = 'extension_services'
    run_after = ['init_extensions', 'services']

    def run_hook(self, app: FlaskUnchained, bundles: List[Bundle]) -> None:
        for ext in app.unchained.extensions.values():
            if not hasattr(ext, 'inject_services'):
                continue

            services = inspect.signature(ext.inject_services).parameters
            ext.inject_services(**{name: app.unchained.services.get(name)
                                   for name in services})
