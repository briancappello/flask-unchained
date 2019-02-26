import inspect
import re

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
    from warnings import warn
    warn('BeautifulSoup4 is not installed. Will not automatically '
         'convert html email messages to plain text.')

try:
    import lxml
except ImportError:
    from warnings import warn
    warn('lxml is not installed. Will not automatically '
         'convert html email messages to plain text.')

from flask import render_template
from flask_mail import Message
from typing import *

from .extensions import mail

message_sig = inspect.signature(Message)
message_kwargs = {name for name, param in message_sig.parameters.items()
                  if (param.kind == param.POSITIONAL_OR_KEYWORD
                      or param.kind == param.KEYWORD_ONLY)}


def get_message_plain_text(msg: Message):
    """
    Converts an HTML message to plain text.

    :param msg: A :class:`~flask_mail.Message`
    :return: The plain text message.
    """
    if msg.body:
        return msg.body

    if BeautifulSoup is None or not msg.html:
        return msg.html

    plain_text = '\n'.join(line.strip() for line in
                           BeautifulSoup(msg.html, 'lxml').text.splitlines())
    return re.sub(r'\n\n+', '\n\n', plain_text).strip()


def make_message(subject_or_message: Union[str, Message],
                 to: Union[str, List[str]],
                 template: Optional[str] = None,
                 **kwargs):
    """
    Creates a new :class:`~flask_mail.Message` from the given arguments.

    :param subject_or_message: A subject string, or for backwards compatibility with
                               stock Flask-Mail, a :class:`~flask_mail.Message` instance
    :param to: An email address, or a list of email addresses
    :param template: Which template to render.
    :param kwargs: Extra kwargs to pass on to :class:`~flask_mail.Message`
    :return: The created :class:`~flask_mail.Message`
    """
    if isinstance(subject_or_message, Message):
        return subject_or_message

    if isinstance(to, tuple):
        to = list(to)
    elif not isinstance(to, list):
        to = [to]
    msg = Message(subject=subject_or_message, recipients=to, **{
        k: kwargs[k] for k in message_kwargs & set(kwargs)})

    if not msg.html and template:
        msg.html = render_template(template, **kwargs)
    if not msg.body:
        msg.body = get_message_plain_text(msg)
    return msg


def _send_mail(subject_or_message: Optional[Union[str, Message]] = None,
               to: Optional[Union[str, List[str]]] = None,
               template: Optional[str] = None,
               **kwargs):
    """
    The default function used for sending emails.

    :param subject_or_message: A subject string, or for backwards compatibility with
                               stock Flask-Mail, a :class:`~flask_mail.Message` instance
    :param to: An email address, or a list of email addresses
    :param template: Which template to render.
    :param kwargs: Extra kwargs to pass on to :class:`~flask_mail.Message`
    """
    subject_or_message = subject_or_message or kwargs.pop('subject')
    to = to or kwargs.pop('recipients', [])
    msg = make_message(subject_or_message, to, template, **kwargs)
    with mail.connect() as connection:
        connection.send(msg)
