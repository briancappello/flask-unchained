from flask_mail import _MailMixin
from flask_unchained import FlaskUnchained
from flask_unchained.utils import ConfigProperty, ConfigPropertyMeta
from types import FunctionType
from typing import *


class Mail(_MailMixin, metaclass=ConfigPropertyMeta):
    """
    The mail extension.
    """

    server: str = ConfigProperty()
    username: Optional[str] = ConfigProperty()
    password: Optional[str] = ConfigProperty()
    port: int = ConfigProperty()
    use_tls: bool = ConfigProperty()
    use_ssl: bool = ConfigProperty()
    default_sender: str = ConfigProperty()
    debug: Union[int, bool] = ConfigProperty()
    max_emails: Optional[int] = ConfigProperty()
    suppress: bool = ConfigProperty('MAIL_SUPPRESS_SEND')
    ascii_attachments: bool = ConfigProperty()

    send: FunctionType = ConfigProperty('MAIL_SEND_FN')

    def send_message(self,
                     subject: Optional[str] = None,
                     to: Optional[Union[str, List[str]]] = None,
                     **kwargs):
        """
        Send an email using the configured :attr:`send` function.

        :param subject: The message subject.
        :param to: The message recipient(s)
        :param kwargs: Extra values to pass on to :class:`~flask_mail.Message`
        """
        to = to or kwargs.pop('recipients', [])
        return self.send(subject, to, **kwargs)

    def init_app(self, app: FlaskUnchained):
        app.extensions['mail'] = self
