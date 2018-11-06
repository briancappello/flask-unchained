"""
code adapted from:
https://stackoverflow.com/questions/12044776/how-to-use-flask-sqlalchemy-in-a-celery-task
"""
import flask

from celery import Celery as BaseCelery
from dill import dumps as dill_dumps, load as dill_load
from kombu.serialization import pickle_loads, pickle_protocol, registry
from kombu.utils.encoding import str_to_bytes


class Celery(BaseCelery):
    """
    The `Celery` extension::

        from flask_unchained.bundles.celery import celery
    """
    def __init__(self, *args, **kwargs):
        self._register_dill()
        super().__init__(*args, **kwargs)
        self.override_task_class()

    def override_task_class(self):
        BaseTask = self.Task
        _celery = self

        class ContextTask(BaseTask):
            abstract = True

            def __call__(self, *args, **kwargs):
                if flask.has_app_context():
                    return BaseTask.__call__(self, *args, **kwargs)
                else:
                    with _celery.app.app_context():
                        return BaseTask.__call__(self, *args, **kwargs)

        self.Task = ContextTask

    def init_app(self, app):
        self.app = app
        self.main = app.import_name
        self.__autoset('broker_url', app.config.CELERY_BROKER_URL)
        self.__autoset('result_backend', app.config.CELERY_RESULT_BACKEND)
        self.config_from_object(app.config)

        # we don't use self.autodiscover_tasks here, preferring instead to allow the
        # DiscoverTasksHook to discover tasks. This way allows for bundles to define
        # what module their tasks are located in (and in a consistent way with how it
        # works for the rest of Flask Unchained)

    def _register_dill(self):
        def encode(obj, dumper=dill_dumps):
            return dumper(obj, protocol=pickle_protocol)

        def decode(s):
            return pickle_loads(str_to_bytes(s), load=dill_load)

        registry.register(
            name='dill',
            encoder=encode,
            decoder=decode,
            content_type='application/x-python-serialize',
            content_encoding='binary'
        )

    # the same as upstream, but we need to copy it here so we can access it
    def __autoset(self, key, value):
        if value:
            self._preconf[key] = value
            self._preconf_set_by_auto.add(key)
