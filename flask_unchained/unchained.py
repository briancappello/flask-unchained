from collections import defaultdict, namedtuple
from datetime import datetime
from flask import Flask
from typing import *

from .bundle import Bundle
from .constants import DEV, PROD, STAGING, TEST
from .di import DependencyInjectionMixin
from .utils import format_docstring


CategoryActionLog = namedtuple('CategoryActionLog',
                               ('category', 'column_names', 'items'))
ActionLogItem = namedtuple('ActionLogItem', ('data', 'timestamp'))
ActionTableItem = namedtuple('ActionTableItem', ('column_names', 'converter'))


class Unchained(DependencyInjectionMixin):
    def __init__(self, env: Optional[Union[DEV, PROD, STAGING, TEST]] = None):
        super().__init__(env)

        self.BUNDLES = []
        self.env = env
        self._bundle_stores = {}
        self._shell_ctx = {}

        self._action_log = defaultdict(list)
        self._action_tables = {}

        self.register_action_table(
            'flask',
            ['app_name', 'root_path', 'kwargs'],
            lambda d: [d['app_name'], d['root_path'], d['kwargs']])

        self.register_action_table(
            'bundle',
            ['name', 'location'],
            lambda bundle: [bundle.name,
                            f'{bundle.__module__}:{bundle.__name__}'])

        self.register_action_table(
            'hook',
            ['Hook Name', 'Default Bundle Module',
             'Bundle Module Override Attr', 'Description'],
            lambda hook: [hook.name,
                          hook.bundle_module_name or '',
                          hook.bundle_override_module_name_attr or '',
                          format_docstring(hook.__doc__)])

    def init_app(self,
                 app: Flask,
                 env: Optional[Union[DEV, PROD, STAGING, TEST]] = None,
                 bundles: Optional[List[Type[Bundle]]] = None,
                 ) -> None:
        self.BUNDLES = bundles
        self.env = env or self.env
        app.extensions['unchained'] = self
        app.unchained = self

        # must import the RunHooksHook here to prevent a circular dependency
        from .hooks.run_hooks_hook import RunHooksHook
        RunHooksHook(self).run_hook(app, bundles or [])

    def log_action(self, category: str, data):
        converter = lambda x: x
        if category in self._action_tables:
            converter = self._action_tables[category].converter
        self._action_log[category].append((converter(data), datetime.now()))

    def register_action_table(self, category: str, columns, converter):
        self._action_tables[category] = ActionTableItem(columns, converter)

    def get_action_log(self, category: str):
        return CategoryActionLog(
            category,
            self._action_tables[category].column_names,
            self._action_log_items_by_category(category))

    def _action_log_items_by_category(self, category: str):
        items = [ActionLogItem(data, timestamp)
                 for data, timestamp in self._action_log[category]]
        return sorted(items, key=lambda row: row.timestamp)

    def __getattr__(self, name: str):
        if name in self._bundle_stores:
            return self._bundle_stores[name]
        raise AttributeError(name)


unchained = Unchained()
