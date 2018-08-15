import pytest

from flask_unchained.bundles.security.decorators import (
    auth_required,
    # roles_accepted,  # tested by tests for auth_required
    # roles_required,  # tested by tests for auth_required
)
from werkzeug.exceptions import Forbidden, Unauthorized


class MethodCalled(Exception):
    pass


@pytest.mark.usefixtures('user')
class TestAuthRequired:
    def test_decorated_with_parenthesis(self):
        @auth_required()
        def method():
            raise MethodCalled

        with pytest.raises(Unauthorized):
            method()

    def test_decorated_without_parenthesis(self):
        @auth_required
        def method():
            raise MethodCalled

        with pytest.raises(Unauthorized):
            method()

    def test_anonymous_user_unauthorized(self):
        @auth_required
        def method():
            raise MethodCalled

        with pytest.raises(Unauthorized):
            method()

    def test_authed_user_allowed(self, client):
        client.login_user()

        @auth_required
        def method():
            raise MethodCalled

        with pytest.raises(MethodCalled):
            method()

    def test_with_role(self, client):
        client.login_user()

        @auth_required(role='ROLE_USER')
        def method():
            raise MethodCalled

        with pytest.raises(MethodCalled):
            method()

    def test_without_role(self, client):
        client.login_user()

        @auth_required(role='ROLE_FAIL')
        def method():
            raise MethodCalled

        with pytest.raises(Forbidden):
            method()

    def test_with_all_roles(self, client):
        client.login_user()

        @auth_required(roles=['ROLE_USER', 'ROLE_USER1'])
        def method():
            raise MethodCalled

        with pytest.raises(MethodCalled):
            method()

    def test_without_all_roles(self, client):
        client.login_user()

        @auth_required(roles=['ROLE_USER', 'ROLE_FAIL'])
        def method():
            raise MethodCalled

        with pytest.raises(Forbidden):
            method()

    def test_with_one_of_roles(self, client):
        client.login_user()

        @auth_required(one_of=['ROLE_USER', 'ROLE_FAIL'])
        def method():
            raise MethodCalled

        with pytest.raises(MethodCalled):
            method()

    def test_without_one_of_roles(self, client):
        client.login_user()

        @auth_required(one_of=['ROLE_FAIL', 'ROLE_ALSO_FAIL'])
        def method():
            raise MethodCalled

        with pytest.raises(Forbidden):
            method()

    def test_with_role_and_one_of_roles(self, client):
        client.login_user()

        @auth_required(role='ROLE_USER', one_of=['ROLE_FAIL', 'ROLE_USER1'])
        def method():
            raise MethodCalled

        with pytest.raises(MethodCalled):
            method()

        @auth_required(roles=['ROLE_USER'], one_of=['ROLE_FAIL', 'ROLE_USER1'])
        def method():
            raise MethodCalled

        with pytest.raises(MethodCalled):
            method()

    def test_without_role_and_one_of_roles(self, client):
        client.login_user()

        @auth_required(role='ROLE_FAIL', one_of=['ROLE_USER'])
        def method():
            raise MethodCalled

        with pytest.raises(Forbidden):
            method()

        @auth_required(roles=['ROLE_FAIL'], one_of=['ROLE_USER'])
        def method():
            raise MethodCalled

        with pytest.raises(Forbidden):
            method()

        @auth_required(role='ROLE_USER', one_of=['ROLE_FAIL'])
        def method():
            raise MethodCalled

        with pytest.raises(Forbidden):
            method()

        @auth_required(roles=['ROLE_USER'], one_of=['ROLE_FAIL'])
        def method():
            raise MethodCalled

        with pytest.raises(Forbidden):
            method()

    def test_only_one_of_role_or_roles_allowed(self, client):
        client.login_user()

        with pytest.raises(RuntimeError) as e:
            @auth_required(role='ROLE_USER', roles=['ROLE_USER1'])
            def method():
                raise MethodCalled
        assert 'specify only one of `role` or `roles` kwargs' in str(e)

    def test_works_with_token_auth(self, client, user):
        client.login_as(user)

        @auth_required(role='ROLE_USER')
        def method():
            raise MethodCalled

        with pytest.raises(MethodCalled):
            method()
