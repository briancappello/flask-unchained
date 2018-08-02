from flask_unchained.cli import cli, click

from .extensions import mail as mail_ext


@cli.group()
def mail():
    """Mail commands"""


@mail.command(name='send-test-email')
@click.option('--subject', help='Message subject',
              default='Hello world from Flask Mail')
@click.option('--to', help='Message recipient')
def send_test_email(subject, to):
    mail_ext.send(subject, to, template='email/__test_email__.html')
