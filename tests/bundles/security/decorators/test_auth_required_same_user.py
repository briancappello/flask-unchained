import pytest

from flask_unchained.bundles.security.decorators import auth_required_same_user
from werkzeug.exceptions import Forbidden


class MethodCalled(Exception):
    pass


@pytest.mark.usefixtures('user', 'admin')
class TestAuthRequiredSameUser:
    def test_different_user_forbidden(self, client, monkeypatch, admin):
        client.login_user()

        monkeypatch.setattr('flask.request.view_args', {'id': admin.id})

        @auth_required_same_user
        def method():
            raise MethodCalled

        with pytest.raises(Forbidden):
            method()

        monkeypatch.undo()

    def test_same_user_allowed(self, client, monkeypatch, user):
        client.login_user()

        monkeypatch.setattr('flask.request.view_args', {'id': user.id})

        @auth_required_same_user
        def method():
            raise MethodCalled

        with pytest.raises(MethodCalled):
            method()

        monkeypatch.undo()

    def test_non_default_parameter_name(self, client, monkeypatch, user):
        client.login_user()

        monkeypatch.setattr('flask.request.view_args', {'user_id': user.id})

        @auth_required_same_user('user_id')
        def method():
            raise MethodCalled

        with pytest.raises(MethodCalled):
            method()

        monkeypatch.undo()

    def test_it_accepts_auth_required_kwargs(self, client, monkeypatch, user):
        client.login_user()

        monkeypatch.setattr('flask.request.view_args', {'id': user.id})

        @auth_required_same_user(role='ROLE_USER')
        def method():
            raise MethodCalled

        with pytest.raises(MethodCalled):
            method()

        @auth_required_same_user(roles=['ROLE_FAIL'])
        def method():
            raise MethodCalled

        with pytest.raises(Forbidden):
            method()

        @auth_required_same_user(one_of=['ROLE_USER', 'ROLE_FAIL'])
        def method():
            raise MethodCalled

        with pytest.raises(MethodCalled):
            method()

        @auth_required_same_user(role='ROLE_USER',
                                 one_of=['ROLE_USER1', 'ROLE_FAIL'])
        def method():
            raise MethodCalled

        with pytest.raises(MethodCalled):
            method()

        monkeypatch.undo()
