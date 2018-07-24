"""
    flask_unchained.bundles.mail
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Adds email sending support to Flask Unchained

    :copyright: Copyright © 2018 Brian Cappello
    :license: MIT, see LICENSE for more details
"""

__version__ = '0.2.1'


from flask_unchained import Bundle

from .extensions import Mail, mail


class MailBundle(Bundle):
    command_group_names = ['mail']
