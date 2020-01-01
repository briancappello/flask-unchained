from flask_unchained import Bundle

from .services import OAuthService
from .views import OAuthController


class OAuthBundle(Bundle):
    """
    The OAuth Bundle.
    """

    name = 'oauth_bundle'
    """
    The name of the OAuth Bundle.
    """
