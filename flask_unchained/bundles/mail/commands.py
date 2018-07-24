import click

from flask.cli import with_appcontext

from .extensions import mail as mail_ext


@click.group()
def mail():
    """Mail commands"""


@mail.command()
@click.argument('subject')
@click.argument('to')
@with_appcontext
def send_test_email(subject, to):
    mail_ext.send(subject, to, template='email/__test_email__.html')
