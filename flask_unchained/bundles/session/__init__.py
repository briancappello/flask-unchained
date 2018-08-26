from flask_unchained import Bundle

from .extensions import Session, session


class SessionBundle(Bundle):
    """
    The :class:`Bundle` subclass for the Session Bundle. Has no special behaviour.
    """
