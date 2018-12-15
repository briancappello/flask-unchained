from flask_unchained import Controller, current_app, request, route, session, url_for, injectable

from ..extensions import OAuth


class OAuthController(Controller):
    oauth: OAuth = injectable

    @route(methods=['GET', 'POST'])
    def login(self):
        return self.oauth.github.authorize(callback=url_for(
            'o_auth_controller.authorized', _external=True, _scheme='https'))

    @route(methods=['GET', 'POST'])
    def logout(self):
        session.pop('oauth_token', None)
        return self.redirect('SECURITY_POST_LOGOUT_REDIRECT_ENDPOINT')

    @route(methods=['GET', 'POST'])
    def authorized(self):
        resp = self.oauth.authorized_response()
        if resp is None or resp.get('access_token') is None:
            return 'Access denied: reason=%s error=%s resp=%s' % (
                request.args['error'],
                request.args['error_description'],
                resp
            )
        session['oauth_token'] = (resp['access_token'], '')
        user = self.oauth.get('user')

        user_login = user.data['login']
        user_email = user.data['email']
        
        return self.redirect('SECURITY_POST_LOGIN_REDIRECT_ENDPOINT')