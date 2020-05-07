# monkeypatch for using flask-oauthlib with werkzeug 1.x
import werkzeug
from werkzeug.http import parse_options_header
from werkzeug.urls import url_decode, url_encode, url_quote
from werkzeug.utils import cached_property
setattr(werkzeug, 'parse_options_header', parse_options_header)
setattr(werkzeug, 'url_decode', url_decode)
setattr(werkzeug, 'url_encode', url_encode)
setattr(werkzeug, 'url_quote', url_quote)
setattr(werkzeug, 'cached_property', cached_property)
# end monkeypatch

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
