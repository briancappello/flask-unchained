import pytest
from flask_unchained.bundles.mail.pytest import *

from flask_mail import Message
from flask_unchained.bundles.mail import mail
from flask_unchained.bundles.mail.utils import _send_mail


subject = 'hello world'
recipient = 'foo@example.com'
sender = 'noreply@example.com'
body = 'one fine body'
html = '''\
<html>
<body>
  <p>one fine body</p>
</body>
</html>'''


@pytest.mark.bundles(['flask_unchained.bundles.mail'])
@pytest.mark.options(MAIL_DEFAULT_SENDER=sender)
class TestMail:
    def test_send_mail(self, outbox, templates):
        _send_mail(subject, recipient, 'send_mail.html')
        assert len(outbox) == len(templates) == 1
        assert templates[0].template.name == 'send_mail.html'
        msg = outbox[0]
        assert msg.subject == subject
        assert msg.recipients == [recipient]
        assert msg.sender == sender
        assert msg.body == body
        assert msg.html == html

    def test_send(self, outbox):
        msg = Message(subject, [recipient], body=body, html=html)
        mail.send(msg)
        assert len(outbox) == 1
        assert outbox[0] == msg
        assert msg.sender == sender

    def test_send_message(self, outbox):
        mail.send_message(subject=subject, recipients=[recipient],
                          body=body, html=html)
        assert len(outbox) == 1
        msg = outbox[0]
        assert msg.subject == subject
        assert msg.recipients == [recipient]
        assert msg.sender == sender
        assert msg.body == body
        assert msg.html == html
