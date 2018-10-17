import os

from flask_unchained import BundleConfig
from flask_unchained.utils import get_boolean_env

from .utils import _send_mail


class Config(BundleConfig):
    """
    Default configuration options for the mail bundle.
    """

    MAIL_SERVER = os.getenv('FLASK_MAIL_SERVER', '127.0.0.1')
    """
    The hostname/IP of the mail server.
    """

    MAIL_PORT = os.getenv('FLASK_MAIL_PORT', 25)
    """
    The port the mail server is running on.
    """

    MAIL_USERNAME = os.getenv('FLASK_MAIL_USERNAME', None)
    """
    The username to connect to the mail server with, if any.
    """

    MAIL_PASSWORD = os.getenv('FLASK_MAIL_PASSWORD', None)
    """
    The password to connect to the mail server with, if any.
    """

    MAIL_USE_TLS = get_boolean_env('FLASK_MAIL_USE_TLS', False)
    """
    Whether or not to use TLS.
    """

    MAIL_USE_SSL = get_boolean_env('FLASK_MAIL_USE_SSL', False)
    """
    Whether or not to use SSL.
    """

    MAIL_DEFAULT_SENDER = os.getenv(
        'FLASK_MAIL_DEFAULT_SENDER',
        f"Flask Mail <noreply@{os.getenv('FLASK_DOMAIN', 'localhost')}>")
    """
    The default sender to use, if none is specified otherwise.
    """

    MAIL_SEND_FN = _send_mail
    """
    The function to use for sending emails. Defaults to
    :func:`~flask_unchained.bundles.mail.utils._send_mail`, and any customized
    send function must implement the same function signature.
    """

    MAIL_DEBUG = 0
    """
    The debug level to set for interactions with the mail server.
    """

    MAIL_MAX_EMAILS = os.getenv('FLASK_MAIL_MAX_EMAILS', None)
    """
    The maximum number of emails to send per connection with the mail server.
    """

    MAIL_SUPPRESS_SEND = False
    """
    Whether or not to actually send emails, or just pretend to. This is mainly
    useful for testing.
    """

    MAIL_ASCII_ATTACHMENTS = os.getenv('FLASK_MAIL_ASCII_ATTACHMENTS', False)
    """
    Whether or not to coerce attachment filenames to ASCII.
    """


class DevConfig(Config):
    """
    Development-specific config options for the mail bundle.
    """

    MAIL_DEBUG = 1
    """
    Set the mail server debug level to 1 in development.
    """

    MAIL_PORT = os.getenv('FLASK_MAIL_PORT', 1025)  # MailHog
    """
    In development, the mail bundle is configured to connect to MailHog.
    """


class ProdConfig(Config):
    """
    Production-specific config options for the mail bundle.
    """

    MAIL_PORT = os.getenv('FLASK_MAIL_PORT', 465)
    """
    In production, the mail bundle is configured to connect using SSL.
    """

    MAIL_USE_SSL = get_boolean_env('FLASK_MAIL_USE_SSL', True)
    """
    Set use SSL to ``True`` in production.
    """


class TestConfig(Config):
    """
    Test-specific config options for the mail bundle.
    """

    MAIL_SUPPRESS_SEND = True
    """
    Do not actually send emails when running tests.
    """


__all__ = [
    'Config',
    'DevConfig',
    'ProdConfig',
    'TestConfig',
]
