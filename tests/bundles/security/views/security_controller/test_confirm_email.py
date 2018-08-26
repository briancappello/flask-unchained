import pytest
from flask_unchained.bundles.mail.pytest import *

from flask_unchained import url_for
from flask_unchained.bundles.security import current_user, AnonymousUser


@pytest.mark.options(SECURITY_CONFIRMABLE=True)
@pytest.mark.user(active=False, confirmed_at=None)
class TestConfirmEmail:
    def test_confirm_email(self, client, registrations, confirmations,
                           user, security_service):
        security_service.register_user(user)
        assert len(registrations) == 1
        assert user == registrations[0]['user']
        assert not user.active
        assert not user.confirmed_at

        confirm_token = registrations[0]['confirm_token']
        r = client.get(url_for('security_controller.confirm_email', token=confirm_token))
        assert r.status_code == 302
        assert r.path == '/'

        assert len(confirmations) == 1
        assert user in confirmations

        assert user.active
        assert user.confirmed_at
        assert current_user == user

    @pytest.mark.options(SECURITY_CONFIRM_EMAIL_WITHIN='-1 seconds')
    def test_expired_token(self, client, user, registrations, confirmations,
                           outbox, templates, security_service):
        security_service.register_user(user)
        assert len(registrations) == 1

        confirm_token = registrations[0]['confirm_token']
        r = client.get(url_for('security_controller.confirm_email', token=confirm_token))
        assert r.status_code == 302
        assert r.path == url_for('security_controller.send_confirmation_email')

        assert len(confirmations) == 0
        assert len(outbox) == len(templates) == 2
        assert templates[0].template.name == 'security/email/welcome.html'
        assert templates[1].template.name == \
               'security/email/email_confirmation_instructions.html'
        assert templates[1].context.get('confirmation_link')

        assert not user.active
        assert not user.confirmed_at
        assert isinstance(current_user._get_current_object(), AnonymousUser)

    def test_invalid_token(self, client, user, registrations, confirmations,
                           outbox, templates, security_service):
        security_service.register_user(user)
        assert len(registrations) == 1

        r = client.get(url_for('security_controller.confirm_email', token='fail'))
        assert r.status_code == 302
        assert r.path == url_for('security_controller.send_confirmation_email')

        assert len(confirmations) == 0
        assert len(outbox) == len(templates) == 1
        assert templates[0].template.name == 'security/email/welcome.html'

        assert not user.active
        assert not user.confirmed_at
        assert isinstance(current_user._get_current_object(), AnonymousUser)
