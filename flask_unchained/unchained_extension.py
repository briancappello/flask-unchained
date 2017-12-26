from collections import defaultdict, namedtuple
from datetime import datetime
from typing import List

from .base_config import AppConfig
from .bundle import Bundle
from .hooks import (ConfigureAppHook, RegisterCommandsHook,
                    RegisterExtensionsHook)
from .utils import AttrGetter, format_docstring


CategoryActionLog = namedtuple('CategoryActionLog',
                               ('category', 'column_names', 'items'))
ActionLogItem = namedtuple('ActionLogItem', ('data', 'timestamp'))
ActionTableItem = namedtuple('ActionTableItem', ('column_names', 'converter'))


class UnchainedStore:
    def __init__(self, app_config_cls):
        self.app_config_cls = app_config_cls
        self.hooks = None

        self._bundle_stores = {}
        self._shell_ctx = {}
        self._extensions = {}
        self.ext = AttrGetter(self._extensions)

        self._action_log = defaultdict(list)
        self._action_tables = {}

        self.register_action_table(
            'bundle',
            ['name', 'location'],
            lambda bundle: [bundle.name,
                            f'{bundle.__module__}:{bundle.__name__}'])

        self.register_action_table(
            'hook',
            ['Priority', 'Name', 'Default Bundle Module',
             'Bundle Module Override Attr', 'Description'],
            lambda hook: [hook.priority,
                          hook.name,
                          hook.bundle_module_name,
                          hook.bundle_override_module_name_attr,
                          format_docstring(hook.__doc__)])

    def log_action(self, category: str, data, timestamp=None):
        converter = lambda x: x
        if category in self._action_tables:
            converter = self._action_tables[category].converter
        self._action_log[category].append((converter(data),
                                           timestamp or datetime.now()))

    def register_action_table(self, category, columns, converter):
        self._action_tables[category] = ActionTableItem(columns, converter)

    def get_action_log(self, category):
        return CategoryActionLog(
            category,
            self._action_tables[category].column_names,
            self._action_log_items_by_category(category))

    def _action_log_items_by_category(self, category):
        items = [ActionLogItem(data, timestamp)
                 for data, timestamp in self._action_log[category]]
        return sorted(items, key=lambda row: row.timestamp)

    def __getattr__(self, name):
        if name in self._bundle_stores:
            return self._bundle_stores[name]
        raise AttributeError(name)


class UnchainedExtension:
    hooks = [ConfigureAppHook, RegisterCommandsHook, RegisterExtensionsHook]

    def init_app(self, app, app_config_cls: AppConfig, bundles: List[Bundle]):
        unchained = UnchainedStore(app_config_cls)
        unchained.hooks = self._load_hooks(unchained, bundles)
        app.extensions['unchained'] = unchained

        for hook in unchained.hooks:
            unchained.log_action('hook', hook)
            if hook.action_category:
                unchained.register_action_table(hook.action_category,
                                                hook.action_table_columns,
                                                hook.action_table_converter)
            hook.run_hook(app, bundles)
            hook.update_shell_context(unchained._shell_ctx)

        app.shell_context_processor(lambda: unchained._shell_ctx)
        return unchained

    def _load_hooks(self, unchained, bundles: List[Bundle]):
        hooks = [(hook.priority, hook(unchained)) for hook in self.hooks]
        for bundle in bundles:
            unchained.log_action('bundle', bundle)
            bundle_store = bundle.store and bundle.store() or None
            if bundle_store:
                unchained._bundle_stores[bundle.name] = bundle_store
            hooks += [(hook.priority, hook(unchained, bundle_store))
                      for hook in bundle.hooks]
        return [hook for _, hook in sorted(hooks, key=lambda pair: pair[0])]
