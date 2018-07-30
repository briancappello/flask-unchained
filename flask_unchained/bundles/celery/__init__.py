"""
    Celery Bundle
    -------------

    Adds Celery support to Flask Unchained
"""

from flask_unchained import Bundle

from .extensions import celery


class CeleryBundle(Bundle):
    command_group_names = ['celery']
