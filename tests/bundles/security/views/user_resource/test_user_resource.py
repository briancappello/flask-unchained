import pytest
from flask_unchained.bundles.mail.pytest import *

from flask_unchained.bundles.security import AnonymousUser, current_user


NEW_USER_DATA = dict(username='new',
                     email='new@example.com',
                     password='password',
                     firstName='new',
                     lastName='user')


@pytest.mark.usefixtures('user')
class TestUserResource:
    def test_get_auth_required(self, api_client, user):
        r = api_client.get('user_resource.get', id=user.id)
        assert r.status_code == 401

    def test_get_same_user_required(self, api_client, admin):
        api_client.login_user()
        r = api_client.get('user_resource.get', id=admin.id)
        assert r.status_code == 403

    def test_get(self, api_client, user):
        api_client.login_user()
        r = api_client.get('user_resource.get', id=user.id)
        assert r.status_code == 200
        assert r.json['id'] == user.id

    def test_patch_auth_required(self, api_client, user):
        r = api_client.patch('user_resource.patch', id=user.id)
        assert r.status_code == 401

    def test_patch_same_user_required(self, api_client, admin):
        api_client.login_user()
        r = api_client.patch('user_resource.patch', id=admin.id)
        assert r.status_code == 403

    def test_patch_different_id_errors(self, api_client, user):
        api_client.login_user()
        r = api_client.patch('user_resource.patch', id=user.id,
                             data=dict(id=42))
        assert r.status_code == 400
        assert 'id' in r.errors

    def test_patch(self, api_client, user):
        api_client.login_user()
        first_name = 'a new name'
        r = api_client.patch('user_resource.patch', id=user.id,
                             data=dict(firstName=first_name))
        assert r.status_code == 200
        assert r.json['firstName'] == first_name
        assert user.first_name == first_name

    def test_create_anonymous_required(self, api_client):
        api_client.login_user()
        r = api_client.post('user_resource.create')
        assert r.status_code == 403

    def test_create_unique_username(self, api_client, user):
        data = NEW_USER_DATA.copy()
        data['username'] = user.username
        r = api_client.post('user_resource.create', data=data)
        assert r.status_code == 400
        assert 'Sorry, that username is already taken.' in r.errors['username']

    def test_create_valid_username(self, api_client):
        data = NEW_USER_DATA.copy()
        data['username'] = '@#$!'
        r = api_client.post('user_resource.create', data=data)
        assert r.status_code == 400
        msg = 'Usernames can only contain letters, ' \
              'numbers, and/or underscore characters.'
        assert msg in r.errors['username']

    def test_create_unique_email(self, api_client, user):
        data = NEW_USER_DATA.copy()
        data['email'] = user.email
        r = api_client.post('user_resource.create', data=data)
        assert r.status_code == 400
        assert 'email' in r.errors

    def test_create_required_validators(self, api_client):
        r = api_client.post('user_resource.create')
        assert r.status_code == 400
        assert 'Email is required.' in r.errors['email']
        assert 'First Name is required.' in r.errors['firstName']
        assert 'Last Name is required.' in r.errors['lastName']
        assert 'Password is required.' in r.errors['password']
        assert 'Username is required.' in r.errors['username']

    @pytest.mark.options(SECURITY_CONFIRMABLE=False)
    def test_create(self, api_client, user_manager, outbox, templates):
        r = api_client.post('user_resource.create', data=NEW_USER_DATA)
        assert r.status_code == 201

        assert 'user' in r.json
        assert 'token' in r.json
        assert current_user == user_manager.get(r.json['user']['id'])

        assert len(outbox) == 1
        assert templates[0].template.name == 'security/email/welcome.html'
        assert not templates[0].context.get('confirmation_link')

    @pytest.mark.options(SECURITY_CONFIRMABLE=True)
    def test_create_confirmable(self, api_client, outbox, templates):
        r = api_client.post('user_resource.create', data=NEW_USER_DATA)
        assert r.status_code == 201, r.json
        assert 'user' in r.json
        assert 'token' not in r.json
        assert isinstance(current_user._get_current_object(), AnonymousUser)
        assert len(outbox) == 1
        assert templates[0].template.name == 'security/email/welcome.html'
        assert templates[0].context.get('confirmation_link')
