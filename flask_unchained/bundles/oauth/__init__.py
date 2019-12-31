from flask_unchained import Bundle

from .services import OAuthService
from .views import OAuthController


class OAuthBundle(Bundle):
    """
    The :class:`~flask_unchained.Bundle` subclass for the OAuth Bundle.
    """

    name = 'oauth_bundle'
