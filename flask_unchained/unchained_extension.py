from collections import defaultdict
from datetime import datetime
from typing import List

from .base_config import AppConfig
from .bundle import Bundle
from .hooks import ConfigureAppHook, RegisterExtensionsHook
from .utils import AttrGetter


class UnchainedStore:
    def __init__(self, app_config_cls):
        self.app_config_cls = app_config_cls
        self._bundle_stores = {}
        self._extensions = {}
        self._shell_ctx = {}
        self._debug_log = defaultdict(list)
        self.ext = AttrGetter(self._extensions)

    def log_msg(self, category, msg):
        self._debug_log[category].append((msg, datetime.now()))

    def get_log(self):
        return [(category, msg, timestamp)
                for category in self._debug_log
                for msg, timestamp in self._debug_log[category]]

    def __getattr__(self, name):
        if name in self._bundle_stores:
            return self._bundle_stores[name]
        raise AttributeError(name)


class UnchainedExtension:
    hooks = [ConfigureAppHook, RegisterExtensionsHook]

    def init_app(self, app, app_config_cls: AppConfig, bundles: List[Bundle]):
        unchained = UnchainedStore(app_config_cls)
        app.extensions['unchained'] = unchained

        for bundle in bundles:
            unchained.log_msg('Bundle', f'{bundle.__class__.__name__} from '
                                        f'{bundle.__module__}')
            if bundle.store:
                unchained._bundle_stores[bundle.name] = bundle.store()

        for hook in self._load_hooks(unchained, bundles):
            unchained.log_msg('Hook', f'(priority {hook.priority:{2}}) '
                                      f'{hook.__class__.__name__} from '
                                      f'{hook.__module__}')
            hook.run_hook(app, bundles)
            hook.update_shell_context(unchained._shell_ctx)

        app.shell_context_processor(lambda: unchained._shell_ctx)
        return unchained

    def _load_hooks(self, unchained, bundles: List[Bundle]):
        hooks = [(hook.priority, hook(unchained)) for hook in self.hooks]
        for bundle in bundles:
            hooks += [(hook.priority, hook(unchained, bundle.name))
                      for hook in bundle.hooks]
        return [hook for _, hook in sorted(hooks, key=lambda pair: pair[0])]
