import pytest
from flask_unchained.bundles.mail.pytest import *


@pytest.mark.options(SECURITY_RECOVERABLE=True)
@pytest.mark.usefixtures('user')
class TestHtmlForgotPassword:
    def test_email_required(self, client, templates):
        r = client.post('security_controller.forgot_password')
        assert r.status_code == 200
        assert templates[0].template.name == 'security/forgot_password.html'
        assert 'Email is required.' in r.html, r.html

    def test_valid_email_required(self, client, templates):
        r = client.post('security_controller.forgot_password',
                        data=dict(email='fail'))
        assert r.status_code == 200
        assert templates[0].template.name == 'security/forgot_password.html'
        assert 'Invalid email address' in r.html
        assert 'Specified user does not exist' in r.html

    def test_anonymous_user_required(self, client, templates):
        client.login_user()
        r = client.post('security_controller.forgot_password')
        assert r.status_code == 302
        assert r.path == '/'
        r = client.follow_redirects(r)
        assert r.status_code == 200
        assert templates[0].template.name == 'site/index.html'

    def test_valid_request(self, user, client, outbox, templates):
        r = client.post('security_controller.forgot_password',
                        data=dict(email=user.email))
        assert r.status_code == 200
        assert len(outbox) == 1
        assert templates[0].template.name == \
               'security/email/reset_password_instructions.html'
        assert templates[0].context.get('reset_link')

        assert templates[1].template.name == 'security/forgot_password.html'
        flash_msg = 'Instructions to reset your password have been sent to ' \
                    f'{user.email}'
        assert flash_msg in r.html


@pytest.mark.options(SECURITY_RECOVERABLE=True)
@pytest.mark.usefixtures('user')
class TestApiForgotPassword:
    def test_email_required(self, api_client):
        r = api_client.post('security_api.forgot_password')
        assert r.status_code == 400
        assert 'Email is required.' in r.errors['email']

    def test_valid_email_required(self, api_client):
        r = api_client.post('security_api.forgot_password',
                            data=dict(email='fail'))
        assert r.status_code == 400
        assert 'Invalid email address.' in r.errors['email']
        assert 'Specified user does not exist.' in r.errors['email']

    def test_anonymous_user_required(self, api_client):
        api_client.login_user()
        r = api_client.post('security_api.forgot_password')
        assert r.status_code == 403

    def test_valid_request(self, user, api_client, outbox, templates):
        r = api_client.post('security_api.forgot_password',
                            data=dict(email=user.email))
        assert r.status_code == 204
        assert len(outbox) == len(templates) == 1
        assert templates[0].template.name == \
           'security/email/reset_password_instructions.html'
        assert templates[0].context.get('reset_link')
