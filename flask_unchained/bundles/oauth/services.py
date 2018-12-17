from flask_oauthlib.client import OAuthRemoteApp
from flask_unchained import BaseService, unchained
from typing import *


@unchained.service('oauth_service')
class OAuthService(BaseService):
    def get_user_details(self, provider: OAuthRemoteApp) -> Tuple[str, dict]:
        """
        For the given ``provider``, return the user's email address and any
        extra data to create the user model with.
        """
        if provider.name == 'amazon':
            data = provider.get('/user/profile').data
            return data['email'], {}

        elif provider.name == 'github':
            data = provider.get('/user').data
            return data['email'], {}

        raise NotImplementedError(f'Unknown OAuth remote app: {provider.name}')

    def on_authorized(self, provider: OAuthRemoteApp) -> None:
        """
        Optional callback to add custom behavior upon OAuth authorized.
        """
        pass
