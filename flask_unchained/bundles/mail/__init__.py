from flask_unchained import Bundle

from .extensions import Mail, mail


class MailBundle(Bundle):
    """
    The :class:`Bundle` subclass for the mail bundle. Has no special behavior.
    """

    command_group_names = ['mail']
