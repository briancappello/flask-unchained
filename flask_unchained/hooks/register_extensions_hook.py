from typing import *

from ..app_factory_hook import AppFactoryHook
from ..bundles import Bundle
from ..flask_unchained import FlaskUnchained


class RegisterExtensionsHook(AppFactoryHook):
    """
    Registers extensions found in bundles with the ``unchained`` extension.
    """

    name = 'register_extensions'
    """
    The name of this hook.
    """

    bundle_module_names = ['extensions']
    """
    The default module this hook loads from.

    Override by setting the ``extensions_module_names`` attribute on your
    bundle class.
    """

    # skipcq: PYL-W0221 (parameters mismatch in overridden method)
    def process_objects(self,
                        app: FlaskUnchained,
                        extensions: Dict[str, object],
                        ) -> None:
        """
        Discover extensions in bundles and register them with the Unchained
        extension.
        """
        for name, extension in extensions.items():
            if name not in self.unchained.extensions:
                if isinstance(extension, (list, tuple)):
                    extension, dependencies = extension
                self.unchained.extensions[name] = extension

    def collect_from_bundle(self, bundle: Bundle) -> Dict[str, object]:
        """
        Collect declared extensions from a bundle hierarchy.
        """
        extensions = {}
        for b in bundle._iter_class_hierarchy():
            for module in self.import_bundle_modules(b):
                extensions.update(getattr(module, 'EXTENSIONS', {}))
        return extensions
