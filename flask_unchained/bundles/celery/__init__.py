"""
    flask_unchained.bundles.celery
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Adds Celery support to Flask Unchained

    :copyright: Copyright © 2018 Brian Cappello
    :license: MIT, see LICENSE for more details
"""

__version__ = '0.2.2'


from flask_unchained import Bundle

from .extensions import celery


class CeleryBundle(Bundle):
    command_group_names = ['celery']
