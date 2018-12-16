from flask import abort, request, session
from flask_unchained import (
    Controller, injectable, lazy_gettext as _, route, url_for)
from http import HTTPStatus

from ..extensions import OAuth


class OAuthController(Controller):
    oauth: OAuth = injectable

    @route('/login/<string:remote_app>')
    def login(self, remote_app):
        provider = getattr(self.oauth, remote_app)
        return provider.authorize(callback=url_for(
            'o_auth_controller.authorized', remote_app=remote_app,
            _external=True, _scheme='https'))

    def logout(self):
        session.pop('oauth_token', None)
        self.flash(_('flask_unchained.bundles.security:flash.logout'),
                   category='success')
        return self.redirect('SECURITY_POST_LOGOUT_REDIRECT_ENDPOINT')

    @route('/authorized/<string:remote_app>')
    def authorized(self, remote_app):
        provider = getattr(self.oauth, remote_app)
        resp = provider.authorized_response()
        if resp is None or resp.get('access_token') is None:
            abort(HTTPStatus.UNAUTHORIZED,
                  'errorCode={error} error={description}'.format(
                      error=request.args['error'],
                      description=request.args['error_description'],
                  ))

        session['oauth_token'] = resp['access_token']

        self.flash(_('flask_unchained.bundles.security:flash.login'),
                   category='success')
        return self.redirect('SECURITY_POST_LOGIN_REDIRECT_ENDPOINT')
