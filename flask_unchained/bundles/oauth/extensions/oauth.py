from flask_oauthlib.client import OAuth as BaseOAuth
from flask_unchained import session

REMOTE_APP_NAME_CONFIG_PREFIX = 'OAUTH_REMOTE_APP_'


class OAuth(BaseOAuth):

    def init_app(self, app):
        super().init_app(app)

        for config_key, remote_app_config in app.config.items():
            if not config_key.startswith(REMOTE_APP_NAME_CONFIG_PREFIX):
                continue

            remote_app_name = config_key[len(
                REMOTE_APP_NAME_CONFIG_PREFIX):].lower()
            remote_app = self.remote_app(remote_app_name,
                                         **remote_app_config,
                                         app_key=f'OAUTH_{remote_app_name}'.upper())

            remote_app.tokengetter(lambda: session.get('oauth_token'))
