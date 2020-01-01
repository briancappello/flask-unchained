from flask_unchained import Bundle

from .extensions import Celery, celery


class CeleryBundle(Bundle):
    """
    The Celery Bundle.
    """

    name = 'celery_bundle'
    """
    The name of the Celery Bundle.
    """

    command_group_names = ['celery']
    """
    Click groups for the Celery Bundle.
    """
