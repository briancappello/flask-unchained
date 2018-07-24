import inspect
import re

try:
    import lxml
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
    from warnings import warn
    warn('BeautifulSoup and/or lxml was not installed. Will not automatically '
         'convert html email messages to plain text.')

from flask import render_template
from flask_mail import Message

from .extensions import mail

message_sig = inspect.signature(Message)
message_kwargs = {name for name, param in message_sig.parameters.items()
                  if (param.kind == param.POSITIONAL_OR_KEYWORD
                      or param.kind == param.KEYWORD_ONLY)}


def get_message_plain_text(msg: Message):
    if msg.body:
        return msg.body

    if BeautifulSoup is None or not msg.html:
        return msg.html

    plain_text = '\n'.join(line.strip() for line in
                           BeautifulSoup(msg.html, 'lxml').text.splitlines())
    return re.sub(r'\n\n+', '\n\n', plain_text).strip()


def make_message(subject_or_message, to, template=None, **kwargs):
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


def _send_mail(subject_or_message=None, to=None, template=None, **kwargs):
    subject_or_message = subject_or_message or kwargs.pop('subject')
    to = to or kwargs.pop('recipients', [])
    msg = make_message(subject_or_message, to, template, **kwargs)
    with mail.connect() as connection:
        connection.send(msg)
