from flask_unchained import Bundle

from .extensions import Celery, celery


class CeleryBundle(Bundle):
    """
    The :class:`Bundle` subclass for the celery bundle. Has no special behavior.
    """
    command_group_names = ['celery']
