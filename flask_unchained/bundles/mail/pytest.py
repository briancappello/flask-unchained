import pytest

from . import mail


@pytest.fixture()
def outbox():
    with mail.record_messages() as messages:
        yield messages
