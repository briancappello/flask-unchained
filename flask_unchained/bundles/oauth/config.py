from flask_unchained import BundleConfig


class Config(BundleConfig):
    OAUTH_REMOTE_APP_GITHUB = dict(
        base_url='https://api.github.com',
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_method='POST',
        authorize_url='https://github.com/login/oauth/authorize',
        request_token_url=None,
        request_token_params={'scope': 'user:email'},
    )

    OAUTH_REMOTE_APP_AMAZON = dict(
        base_url='https://api.amazon.com',
        access_token_url='https://api.amazon.com/auth/o2/token',
        access_token_method='POST',
        authorize_url='https://www.amazon.com/ap/oa',
        request_token_url=None,
        request_token_params={'scope': 'profile:email'},
    )
