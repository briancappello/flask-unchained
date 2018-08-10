from flask_unchained import Bundle

from .extensions import Mail, mail


class MailBundle(Bundle):
    command_group_names = ['mail']
