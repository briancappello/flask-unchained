"""
Celery Bundle
-------------

Adds Celery support to Flask Unchained.

.. autoclass:: CeleryBundle
    :members:

.. automodule:: flask_unchained.bundles.celery.config

.. automodule:: flask_unchained.bundles.celery.commands

.. automodule:: flask_unchained.bundles.celery.tasks
"""

from flask_unchained import Bundle

from .extensions import celery


class CeleryBundle(Bundle):
    """
    The :class:`Bundle` subclass for the celery bundle. Has no special behavior.
    """
    command_group_names = ['celery']
