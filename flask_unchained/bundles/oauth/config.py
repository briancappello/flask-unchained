from flask_unchained import BundleConfig


class Config(BundleConfig):
    """
    Default configuration settings for the OAuth Bundle.
    """

    pass


class TestConfig(Config):
    """
    Default test settings for the OAuth Bundle.
    """

    OAUTH_REMOTE_APP_GITHUB = dict(
        # these are the kwargs that get passed to `OAuth.register_app`
        consumer_key='a11a1bda412d928fb39a',
        consumer_secret='92b7cf30bc42c49d589a10372c3f9ff3bb310037',
        request_token_params={'scope': 'user:email'},
        base_url='https://api.github.com/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize'
    )
