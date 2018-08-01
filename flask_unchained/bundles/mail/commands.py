import click

from flask.cli import with_appcontext

from .extensions import mail as mail_ext


@click.group()
def mail():
    """Mail commands"""


@mail.command(name='send-test-email')
@click.option('--subject', help='Message subject',
              default='Hello world from Flask Mail')
@click.option('--to', help='Message recipient')
@with_appcontext
def send_test_email(subject, to):
    mail_ext.send(subject, to, template='email/__test_email__.html')
