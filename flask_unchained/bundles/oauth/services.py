from flask_unchained import BaseService, unchained


@unchained.service('oauth_service')
class OAuthService(BaseService):
    def on_authorized(self, provider):
        pass
