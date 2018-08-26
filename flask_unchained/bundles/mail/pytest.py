import pytest

from .extensions import mail


@pytest.fixture()
def outbox():
    """
    Fixture to record which messages got sent by the mail extension (if any).
    Example Usage::

        def test_some_view(client, outbox):
            r = client.get('some.endpoint.that.sends.mail')
            assert len(outbox) == 1
            assert outbox[0].subject == "You've got mail!"
    """
    with mail.record_messages() as messages:
        yield messages
