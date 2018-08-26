import pytest
from flask_unchained.bundles.mail.pytest import *

from tests.bundles.security._bundles.security.forms import RegisterForm


@pytest.mark.options(SECURITY_REGISTERABLE=True,
                     SECURITY_REGISTER_FORM=RegisterForm)
class TestRegister:
    def test_get(self, client, templates):
        r = client.get('security_controller.register')
        assert r.status_code == 200
        assert templates[0].template.name == 'security/register.html'

    def test_errors(self, client, templates):
        r = client.post('security_controller.register', data=dict(
            email='!@#!.com',
        ))
        assert r.status_code == 200
        assert templates[0].template.name == 'security/register.html'
        assert 'Invalid email address.' in r.html
        assert 'Password is required.' in r.html, r.html

    def test_min_password_length(self, client, templates):
        r = client.post('security_controller.register', data=dict(
            email='hello@example.com',
            password='short',
            password_confirm='short',
        ))
        assert r.status_code == 200
        assert templates[0].template.name == 'security/register.html'
        assert 'Password must be at least 8 characters long' in r.html

    @pytest.mark.options(SECURITY_CONFIRMABLE=True)
    def test_register_confirmation_required(self, client, templates, outbox):
        r = client.post('security_controller.register', data=dict(
            username='hello',
            email='hello@example.com',
            password='password',
            password_confirm='password',
            first_name='first',
            last_name='last',
        ))
        assert r.status_code == 302
        assert r.path == '/'
        assert templates[0].template.name == 'security/email/welcome.html'
        assert outbox[0].recipients == ['hello@example.com']
        assert 'Please confirm your email' in outbox[0].html

    @pytest.mark.options(SECURITY_CONFIRMABLE=False)
    def test_register(self, client, templates, outbox):
        r = client.post('security_controller.register', data=dict(
            username='hello',
            email='hello@example.com',
            password='password',
            password_confirm='password',
            first_name='first',
            last_name='last',
        ))
        assert r.status_code == 302
        assert r.path == '/'
        assert templates[0].template.name == 'security/email/welcome.html'
        assert outbox[0].recipients == ['hello@example.com']
        assert 'You may now login at' in outbox[0].html
