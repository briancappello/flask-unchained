import pytest
from flask_unchained.bundles.mail.pytest import *


@pytest.mark.options(SECURITY_CONFIRMABLE=True)
class TestHtmlSendConfirmationEmail:
    def test_email_required(self, client, templates):
        r = client.post('security_controller.send_confirmation_email')
        assert r.status_code == 200
        assert templates[0].template.name == \
               'security/send_confirmation_email.html'
        assert 'Email is required.' in r.html, r.html

    def test_cannot_reconfirm(self, user, client, templates):
        r = client.post('security_controller.send_confirmation_email',
                        data=dict(email=user.email))
        assert r.status_code == 200
        assert templates[0].template.name == \
               'security/send_confirmation_email.html'
        assert 'Your email has already been confirmed.' in r.html

    @pytest.mark.user(confirmed_at=None)
    def test_instructions_resent(self, client, user, outbox, templates,
                                 security_service):
        security_service.register_user(user)
        assert len(outbox) == len(templates) == 1
        assert templates[0].template.name == 'security/email/welcome.html'

        # have them request a new confirmation email
        r = client.post('security_controller.send_confirmation_email',
                        data=dict(email=user.email))

        # make sure they get emailed a new confirmation token
        assert len(outbox) == 2
        assert len(templates) == 3
        assert templates[1].template.name == \
               'security/email/email_confirmation_instructions.html'
        assert templates[0].context.get('confirmation_link') != \
               templates[1].context.get('confirmation_link')

        # make sure the frontend tells them to check their email
        assert r.status_code == 200
        assert templates[2].template.name == \
               'security/send_confirmation_email.html'
        msg = f'Confirmation instructions have been sent to {user.email}'
        assert msg in r.html


@pytest.mark.options(SECURITY_CONFIRMABLE=True)
class TestApiSendConfirmationEmail:
    def test_email_required(self, api_client):
        r = api_client.post('security_api.send_confirmation_email')
        assert r.status_code == 400
        assert 'Email is required.' in r.errors['email']

    def test_cannot_reconfirm(self, user, api_client):
        r = api_client.post('security_api.send_confirmation_email',
                            data=dict(email=user.email))
        assert r.status_code == 400
        assert 'Your email has already been confirmed.' in r.errors['email']

    @pytest.mark.options(SECURITY_CONFIRMABLE=True)
    @pytest.mark.user(confirmed_at=None)
    def test_instructions_resent(self, api_client, user, outbox, templates,
                                 security_service):
        security_service.register_user(user)
        assert len(outbox) == len(templates) == 1

        # have them request a new confirmation email
        r = api_client.post('security_api.send_confirmation_email',
                            data=dict(email=user.email))
        assert r.status_code == 204

        # make sure they get emailed a new confirmation token
        assert len(outbox) == len(templates) == 2
        assert templates[1].template.name == \
               'security/email/email_confirmation_instructions.html'
        assert templates[0].context.get('confirmation_link') != \
               templates[1].context.get('confirmation_link')
