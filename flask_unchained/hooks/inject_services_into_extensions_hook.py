import inspect

from ..app_factory_hook import AppFactoryHook


class InjectServicesIntoExtensions(AppFactoryHook):
    name = 'extension_services'
    bundle_module_name = None
    priority = 70

    def run_hook(self, app, bundles):
        for ext in app.unchained.extensions.values():
            if not hasattr(ext, 'inject_services'):
                continue

            services = inspect.signature(ext.inject_services).parameters
            ext.inject_services(**{name: app.unchained.services.get(name)
                                   for name in services})
