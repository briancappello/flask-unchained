from flask_unchained import Bundle

from .extensions import Session, session


class SessionBundle(Bundle):
    """
    The Session Bundle. Integrates
    `Flask Session <https://pythonhosted.org/Flask-Session/>`_ with Flask Unchained.
    """
    _has_views = False
