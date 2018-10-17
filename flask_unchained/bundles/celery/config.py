import os

from flask_unchained import BundleConfig

from .tasks import async_mail_task, _send_mail_async


class Config(BundleConfig):
    """
    Default configuration options for the Celery Bundle.
    """

    CELERY_BROKER_URL = 'redis://{host}:{port}/0'.format(
        host=os.getenv('FLASK_REDIS_HOST', '127.0.0.1'),
        port=os.getenv('FLASK_REDIS_PORT', 6379),
    )
    """
    The broker URL to connect to.
    """

    CELERY_RESULT_BACKEND = CELERY_BROKER_URL
    """
    The result backend URL to connect to.
    """

    CELERY_ACCEPT_CONTENT = ('json', 'pickle', 'dill')
    """
    Tuple of supported serialization strategies.
    """

    # configure mail bundle to send emails via celery
    # NOTE: the celery bundle must be listed *after* the mail bundle in the user's
    # unchained_config in order for this to work
    if async_mail_task:
        MAIL_SEND_FN = _send_mail_async
