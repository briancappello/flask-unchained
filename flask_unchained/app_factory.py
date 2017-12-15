import inspect

from flask import Flask
from typing import List

from .bundle import Bundle
from .app_factory_hook import AppFactoryHook
from .hooks import (
    ConfigureAppHook,
    RegisterExtensionsHook,
    RegisterDeferredExtensionsHook,
)
from .utils import get_boolean_env, safe_import_module


class AppFactory:
    hooks = [ConfigureAppHook,
             RegisterExtensionsHook,
             RegisterDeferredExtensionsHook]

    def __init__(self, app_config_cls):
        self.app_config_cls = app_config_cls
        self.verbose = get_boolean_env('FLASK_UNCHAINED_VERBOSE', False)
        self.debug(f'Using {app_config_cls.__name__} from '
                   f'{app_config_cls.__module__}')

    def create_app(self, **flask_kwargs) -> Flask:
        bundles = self._load_bundles()
        app = self.instantiate_app(bundles[0].module_name, **flask_kwargs)

        for bundle in bundles:
            self.debug(f'Loading {bundle.__class__.__name__} from '
                       f'{bundle.__module__}')

        hooks = self._load_hooks(bundles)
        for hook in hooks:
            self.debug(f'Running hook: (priority {hook.priority:{2}}) '
                       f'{hook.__class__.__name__} from {hook.__module__}')
            hook.run_hook(app, self.app_config_cls, bundles)

        self.update_shell_context(app, hooks)
        self.configure_app(app)

        return app

    def instantiate_app(self, app_import_name, **flask_kwargs):
        for k, v in getattr(self.app_config_cls, 'FLASK_KWARGS', {}).items():
            if k not in flask_kwargs:
                flask_kwargs[k] = v

        self.debug(f'Creating Flask(app_import_name={app_import_name!r}, '
                   f'kwargs={flask_kwargs!r})')

        return Flask(app_import_name, **flask_kwargs)

    def update_shell_context(self, app: Flask, hooks: List[AppFactoryHook]):
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

    def _load_bundles(self) -> List[Bundle]:
        bundles = []

        for i, bundle_module_name in enumerate(self.app_config_cls.BUNDLES):
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

    def _load_hooks(self, bundles: List[Bundle]) -> List[AppFactoryHook]:
        def make_hooks(hooks):
            return [(hook.priority, hook()) for hook in hooks]

        hooks = make_hooks(self.hooks)
        for bundle in bundles:
            hooks += make_hooks(bundle.hooks)

        return [hook for _, hook in sorted(hooks, key=lambda pair: pair[0])]

    def debug(self, msg: str):
        if self.verbose:
            for line in msg.splitlines():
                print('UNCHAINED:', line)
