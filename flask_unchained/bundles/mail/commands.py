from flask_unchained.cli import cli, click

from .extensions import mail as mail_ext


@cli.group()
def mail():
    """
    Mail commands.
    """


@mail.command(name='send-test-email')
@click.option('--to', prompt='To',
              help='Email address of the recipient.')
@click.option('--subject', prompt='Subject', default='Hello world from Flask Mail',
              help='Email subject.')
def send_test_email(to, subject):
    """
    Attempt to send a test email to the given email address.
    """
    mail_ext.send(subject, to, template='email/__test_email__.html')
