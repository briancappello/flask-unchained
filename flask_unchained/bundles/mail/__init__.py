"""
    Mail Bundle
    -----------

    Adds email sending support to Flask Unchained
"""

from flask_unchained import Bundle

from .extensions import Mail, mail


class MailBundle(Bundle):
    command_group_names = ['mail']
