from flask_unchained import AppFactoryHook, FlaskUnchained
from typing import *


class DiscoverTasksHook(AppFactoryHook):
    """
    Discovers celery tasks.
    """
    name = 'celery_tasks'
    bundle_module_name = 'tasks'
    bundle_override_module_name_attr = 'celery_tasks_module_name'
    run_after = ['init_extensions']

    def process_objects(self, app: FlaskUnchained, objects: Dict[str, Any]):
        # don't need to do anything, just make sure the tasks modules get imported
        # (which happens just by this hook running)
        pass

    def type_check(self, obj: Any):
        return False
