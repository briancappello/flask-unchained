from flask import current_app

from .extensions import celery
from ..mail.extensions import mail
from ..mail.utils import make_message


def _send_mail_async(subject_or_message=None, to=None, template=None, **kwargs):
    subject_or_message = subject_or_message or kwargs.pop('subject')
    if current_app and current_app.testing:
        return async_mail_task.apply([subject_or_message, to, template], kwargs)
    return async_mail_task.delay(subject_or_message, to, template, **kwargs)


@celery.task(serializer='dill')
def async_mail_task(subject_or_message, to=None, template=None, **kwargs):
    """
    Celery task to send emails asynchronously using the mail bundle.
    """
    to = to or kwargs.pop('recipients', [])
    msg = make_message(subject_or_message, to, template, **kwargs)
    with mail.connect() as connection:
        connection.send(msg)
