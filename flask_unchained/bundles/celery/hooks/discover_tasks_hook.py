from flask_unchained import AppFactoryHook, FlaskUnchained
from typing import *


class DiscoverTasksHook(AppFactoryHook):
    """
    Discovers celery tasks.
    """

    name = 'celery_tasks'
    """
    The name of this hook.
    """

    bundle_module_names = ['tasks']
    """
    The default module this hook loads from.

    Override by setting the ``celery_tasks_module_names`` attribute on your
    bundle class.
    """

    bundle_override_module_names_attr = 'celery_tasks_module_names'
    run_after = ['init_extensions']

    def process_objects(self, app: FlaskUnchained, objects: Dict[str, Any]):
        # don't need to do anything, just make sure the tasks modules get imported
        # (which happens just by this hook running)
        pass

    def type_check(self, obj: Any):
        return False
