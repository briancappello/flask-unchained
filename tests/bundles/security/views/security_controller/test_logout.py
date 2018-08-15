import pytest

from flask_unchained import url_for
from flask_unchained.bundles.security import AnonymousUser, current_user


@pytest.mark.usefixtures('user')
class TestLogout:
    def test_html_get(self, client):
        client.login_user()
        r = client.get('security_controller.logout')
        assert r.status_code == 302
        assert r.path == url_for('SECURITY_POST_LOGOUT_REDIRECT_ENDPOINT')
        assert isinstance(current_user._get_current_object(), AnonymousUser)

    def test_api_get(self, api_client):
        api_client.login_user()
        r = api_client.get('security_api.logout')
        assert r.status_code == 204
        assert isinstance(current_user._get_current_object(), AnonymousUser)
