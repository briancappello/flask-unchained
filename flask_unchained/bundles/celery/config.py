import os

from .tasks import async_mail_task, _send_mail_async


class Config:
    CELERY_BROKER_URL = 'redis://{host}:{port}/0'.format(
        host=os.getenv('FLASK_REDIS_HOST', '127.0.0.1'),
        port=os.getenv('FLASK_REDIS_PORT', 6379),
    )
    CELERY_RESULT_BACKEND = CELERY_BROKER_URL
    CELERY_ACCEPT_CONTENT = ('json', 'pickle', 'dill')

    # configure mail bundle to send emails via celery
    if async_mail_task:
        MAIL_SEND_FN = _send_mail_async
