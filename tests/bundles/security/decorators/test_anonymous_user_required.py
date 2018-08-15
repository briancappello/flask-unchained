import pytest

from flask import session
from flask_unchained import url_for
from flask_unchained.bundles.security.decorators import anonymous_user_required
from werkzeug.exceptions import Forbidden


class MethodCalled(Exception):
    pass


@pytest.mark.usefixtures('user')
class TestAnonymousUserRequired:
    def test_decorated_with_without_parenthesis(self):
        @anonymous_user_required()
        def method():
            raise MethodCalled

        with pytest.raises(MethodCalled):
            method()

        @anonymous_user_required
        def method():
            raise MethodCalled

        with pytest.raises(MethodCalled):
            method()

    def test_authed_user_api_request_forbidden(self, client, monkeypatch):
        client.login_user()

        # really we're mocking flask.request.is_json to True, but for some
        # reason, monkeypatch shits a brick trying to mock @property attrs
        monkeypatch.setattr('flask.request._parsed_content_type',
                            ['application/json'])

        @anonymous_user_required
        def method():
            raise MethodCalled

        with pytest.raises(Forbidden):
            method()

        monkeypatch.undo()

    def test_authed_user_html_request_redirected(self, client):
        client.login_user()

        @anonymous_user_required
        def method():
            return None

        r = method()
        assert r.status_code == 302
        assert r.location == url_for('SECURITY_POST_LOGIN_REDIRECT_ENDPOINT')

    def test_custom_params(self, client):
        client.login_user()

        @anonymous_user_required(msg='must be anon', category='error',
                                 redirect_url='/must-be-anon')
        def method():
            return None

        r = method()
        assert r.status_code == 302
        assert r.location == '/must-be-anon'
        assert ('error', 'must be anon') in session['_flashes']

    def test_anonymous_user_allowed(self):
        @anonymous_user_required
        def method():
            raise MethodCalled

        with pytest.raises(MethodCalled):
            method()
