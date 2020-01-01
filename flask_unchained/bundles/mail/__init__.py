from flask_unchained import Bundle

from .extensions import Mail, mail


class MailBundle(Bundle):
    """
    The Mail Bundle.
    """

    name = 'mail_bundle'
    """
    The name of the Mail Bundle.
    """

    command_group_names = ['mail']
    """
    Click groups for the Mail Bundle.
    """
