from flask import abort, request, session
from flask_unchained import (
    Controller, injectable, lazy_gettext as _, route, url_for)
from http import HTTPStatus

from ...security import SecurityService, UserManager, anonymous_user_required

from ..extensions import OAuth
from ..services import OAuthService


class OAuthController(Controller):
    oauth: OAuth = injectable
    oauth_service: OAuthService = injectable
    security_service: SecurityService = injectable
    user_manager: UserManager = injectable

    @route('/login/<string:remote_app>')
    @anonymous_user_required(msg='You are already logged in', category='success')
    def login(self, remote_app):
        provider = getattr(self.oauth, remote_app)
        return provider.authorize(callback=url_for(
            'o_auth_controller.authorized', remote_app=remote_app,
            _external=True, _scheme='https'))

    def logout(self):
        session.pop('oauth_token', None)
        self.security_service.logout_user()
        self.flash(_('flask_unchained.bundles.security:flash.logout'),
                   category='success')
        return self.redirect('SECURITY_POST_LOGOUT_REDIRECT_ENDPOINT')

    @route('/authorized/<string:remote_app>')
    @anonymous_user_required(msg='You are already logged in', category='success')
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

        email, data = self.oauth_service.get_user_details(provider)
        user, created = self.user_manager.get_or_create(email=email,
                                                        defaults=data,
                                                        commit=True)
        if created:
            self.security_service.register_user(
                user, _force_login_without_confirmation=True)
        else:
            self.security_service.login_user(user, force=True)

        self.oauth_service.on_authorized(provider)
        self.flash(_('flask_unchained.bundles.security:flash.login'),
                   category='success')
        return self.redirect('SECURITY_POST_LOGIN_REDIRECT_ENDPOINT')
