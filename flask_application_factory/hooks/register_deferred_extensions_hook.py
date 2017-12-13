from .register_extensions_hook import RegisterExtensionsHook


class RegisterDeferredExtensionsHook(RegisterExtensionsHook):
    priority = 60

    def collect_from_bundle(self, bundle):
        module = self.import_bundle_module(bundle)
        if not module:
            return []

        return self.get_extension_tuples(
            getattr(module, 'DEFERRED_EXTENSIONS', {}))
