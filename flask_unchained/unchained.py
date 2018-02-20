from collections import defaultdict, namedtuple
from datetime import datetime
from flask import Flask
from typing import List, Optional, Type

from .app_config import AppConfig
from .bundle import Bundle
from .utils import AttrGetter, format_docstring


CategoryActionLog = namedtuple('CategoryActionLog',
                               ('category', 'column_names', 'items'))
ActionLogItem = namedtuple('ActionLogItem', ('data', 'timestamp'))
ActionTableItem = namedtuple('ActionTableItem', ('column_names', 'converter'))


class Unchained:
    def __init__(self, app_config_cls: Optional[Type[AppConfig]]=None):
        self.app_config_cls = app_config_cls
        self._bundle_stores = {}
        self._shell_ctx = {}
        self._extensions = {}
        self.ext = AttrGetter(self._extensions)

        self._action_log = defaultdict(list)
        self._action_tables = {}

        self.register_action_table(
            'flask',
            ['app_name', 'kwargs'],
            lambda d: [d['app_name'], d['kwargs']])

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

    def init_app(self,
                 app: Flask,
                 app_config_cls: Optional[Type[AppConfig]]=None,
                 bundles: Optional[List[Bundle]]=None):
        self.app_config_cls = app_config_cls or self.app_config_cls
        app.extensions['unchained'] = self

        # must import the RunHooksHook here to prevent a circular dependency
        from .hooks import RunHooksHook
        RunHooksHook(self).run_hook(app, bundles or [])

    def log_action(self, category: str, data):
        converter = lambda x: x
        if category in self._action_tables:
            converter = self._action_tables[category].converter
        self._action_log[category].append((converter(data), datetime.now()))

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


unchained = Unchained()
