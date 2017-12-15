import inspect

from flask import Flask
from typing import List

from .bundle import Bundle
from .factory_hook import FactoryHook
from .hooks import (
    ConfigureAppHook,
    RegisterExtensionsHook,
    RegisterDeferredExtensionsHook,
)
from .utils import safe_import_module


class FlaskApplicationFactory:
    hooks = [ConfigureAppHook,
             RegisterExtensionsHook,
             RegisterDeferredExtensionsHook]

    def create_app(self, app_config_cls, **flask_kwargs) -> Flask:
        bundles = self._load_bundles(app_config_cls)
        app = self.instantiate_app(bundles[0].module_name,
                                   app_config_cls,
                                   **flask_kwargs)
        hooks = self._load_hooks(bundles)
        for hook in hooks:
            hook.run_hook(app, app_config_cls, bundles)
        self.update_shell_context(app, hooks)
        self.configure_app(app)
        return app

    def instantiate_app(self, app_import_name, app_config_cls, **flask_kwargs):
        for k, v in getattr(app_config_cls, 'FLASK_KWARGS', {}).items():
            if k not in flask_kwargs:
                flask_kwargs[k] = v

        return Flask(app_import_name, **flask_kwargs)

    def update_shell_context(self, app: Flask, hooks: List[FactoryHook]):
        ctx = {}
        for hook in hooks:
            hook.update_shell_context(ctx)
        app.shell_context_processor(lambda: ctx)

    def configure_app(self, app: Flask):
        """
        Implement to add custom configuration to your app, e.g. loading Jinja
        extensions or adding request-response-cycle callback functions
        """
        pass

    def _load_bundles(self, app_config_cls) -> List[Bundle]:
        bundles = []

        for i, bundle_module_name in enumerate(app_config_cls.BUNDLES):
            module = safe_import_module(bundle_module_name)
            bundle_found = False
            for name, bundle in inspect.getmembers(module, self.is_bundle_cls):
                if not bundle.__subclasses__():
                    bundles.append(bundle())
                    bundle_found = True
                # else: FIXME set bundle_found true?

            if not bundle_found:
                raise Exception(
                    f'Unable to find a Bundle subclass for the '
                    f'{bundle_module_name} bundle! Please make sure it\'s '
                    f'installed and that there is a Bundle subclass in the '
                    f'module\'s __init__.py file.')
            elif i == 0 and not bundles[0].app_bundle:
                raise Exception('The first bundle in the BUNDLES app config '
                                'must have app_bundle = True')
            elif i != 0 and bundles[-1].app_bundle:
                raise Exception(f'Cannot have more than one app_bundle '
                                f'({bundles[-1]} conflicts with {bundles[0]})')

        return bundles

    def is_bundle_cls(self, obj):
        if not inspect.isclass(obj):
            return False
        return issubclass(obj, Bundle) and obj != Bundle

    def _load_hooks(self, bundles: List[Bundle]) -> List[FactoryHook]:
        def make_hooks(hooks):
            return [(hook.priority, hook()) for hook in hooks]

        hooks = make_hooks(self.hooks)
        for bundle in bundles:
            hooks += make_hooks(bundle.hooks)

        return [hook for _, hook in sorted(hooks, key=lambda pair: pair[0])]
