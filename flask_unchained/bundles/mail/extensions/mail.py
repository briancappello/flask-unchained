from flask_mail import _MailMixin, Message
from flask_unchained import FlaskUnchained
from flask_unchained.utils import ConfigProperty, ConfigPropertyMetaclass
from types import FunctionType
from typing import *


class Mail(_MailMixin, metaclass=ConfigPropertyMetaclass):
    """
    The `Mail` extension::

        from flask_unchained.bundles.mail import mail
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
                     subject_or_message: Optional[Union[Message, str]] = None,
                     to: Optional[Union[str, List[str]]] = None,
                     **kwargs):
        """
        Send an email using the send function as configured by
        :attr:`~flask_unchained.bundles.mail.config.Config.MAIL_SEND_FN`.

        :param subject_or_message: The subject line, or an instance of
                                   :class:`flask_mail.Message`.
        :param to: The message recipient(s).
        :param kwargs: Extra values to pass on to :class:`~flask_mail.Message`
        """
        to = to or kwargs.pop('recipients', [])
        return self.send(subject_or_message, to, **kwargs)

    def init_app(self, app: FlaskUnchained):
        app.extensions['mail'] = self
