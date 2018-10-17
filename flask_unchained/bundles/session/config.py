import os

from datetime import timedelta
from flask_unchained import BundleConfig

try:
    from flask_unchained.bundles.sqlalchemy import db
except ImportError:
    db = None


class _DefaultFlaskConfigForSessions(BundleConfig):
    SESSION_COOKIE_NAME = 'session'
    """
    The name of the session cookie.

    Defaults to ``'session'``.
    """

    SESSION_COOKIE_DOMAIN = None
    """
    The domain for the session cookie. If this is not set, the cookie will be
    valid for all subdomains of ``SERVER_NAME``.

    Defaults to ``None``.
    """

    SESSION_COOKIE_PATH = None
    """
    The path for the session cookie. If this is not set the cookie will be valid
    for all of ``APPLICATION_ROOT`` or if that is not set for '/'.

    Defaults to ``None``.
    """

    SESSION_COOKIE_HTTPONLY = True
    """
    Controls if the cookie should be set with the ``httponly`` flag. Browsers will
    not allow JavaScript access to cookies marked as ``httponly`` for security.

    Defaults to ``True``.
    """

    SESSION_COOKIE_SECURE = False
    """
    Controls if the cookie should be set with the ``secure`` flag. Browsers will
    only send cookies with requests over HTTPS if the cookie is marked ``secure``.
    The application must be served over HTTPS for this to make sense.

    Defaults to ``False``.
    """

    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    """
    The lifetime of a permanent session as ``datetime.timedelta`` object or an
    integer representing seconds.

    Defaults to 31 days.
    """

    SESSION_COOKIE_SAMESITE = None
    """
    Restrict how cookies are sent with requests from external sites. Limits the
    scope of the cookie such that it will only be attached to requests if those
    requests are "same-site". Can be set to ``'Lax'`` (recommended) or ``'Strict'``.

    Defaults to ``None``.
    """

    SESSION_REFRESH_EACH_REQUEST = True
    """
    Controls the set-cookie behavior. If set to ``True`` a permanent session will
    be refreshed each request and get their lifetime extended, if set to ``False``
    it will only be modified if the session actually modifies. Non permanent sessions
    are not affected by this and will always expire if the browser window closes.

    Defaults to ``True``.
    """


class Config(_DefaultFlaskConfigForSessions):
    """
    Default configuration options for the Session Bundle.
    """

    SESSION_TYPE = 'null'
    """
    Specifies which type of session interface to use. Built-in session types:

    - ``'null'``: :class:`~flask_unchained.bundles.session.session_interfaces.NullSessionInterface` (default)
    - ``'redis'``: :class:`~flask_unchained.bundles.session.session_interfaces.RedisSessionInterface`
    - ``'memcached'``: :class:`~flask_unchained.bundles.session.session_interfaces.MemcachedSessionInterface`
    - ``'filesystem'``: :class:`~flask_unchained.bundles.session.session_interfaces.FileSystemSessionInterface`
    - ``'mongodb'``: :class:`~flask_unchained.bundles.session.session_interfaces.MongoDBSessionInterface`
    - ``'sqlalchemy'``: :class:`~flask_unchained.bundles.session.session_interfaces.SqlAlchemySessionInterface`

    Defaults to ``'null'``.
    """

    SESSION_PERMANENT = True
    """
    Whether use permanent session or not.

    Defaults to ``True``.
    """

    SESSION_USE_SIGNER = False
    """
    Whether sign the session cookie sid or not. If set to ``True``, you have to
    set ``SECRET_KEY``.

    Defaults to ``False``.
    """

    SESSION_KEY_PREFIX = 'session:'
    """
    A prefix that is added before all session keys. This makes it possible to use
    the same backend storage server for different apps.

    Defaults to ``'session:'``.
    """

    SESSION_REDIS = None
    """
    A :class:`redis.Redis` instance.
 
    By default, connect to ``127.0.0.1:6379``.
    """

    SESSION_MEMCACHED = None
    """
    A :class:`memcached.Client` instance.
 
    By default, connect to ``127.0.0.1:11211``.
    """

    SESSION_FILE_DIR = os.path.join(os.getcwd(), 'flask_sessions')
    """
    The folder where session files are stored.

    Defaults to using a folder named ``flask_sessions`` in your current working
    directory.
    """

    SESSION_FILE_THRESHOLD = 500
    """
    The maximum number of items the session stores before it starts deleting some.
 
    Defaults to 500.
    """

    SESSION_FILE_MODE = 0o600
    """
    The file mode wanted for the session files. Should be specified as an octal,
    eg ``0o600``.

    Defaults to ``0o600``.
    """

    SESSION_MONGODB = None
    """
    A :class:`pymongo.MongoClient` instance.

    By default, connect to ``127.0.0.1:27017``.
    """

    SESSION_MONGODB_DB = 'flask_session'
    """
    The MongoDB database you want to use.

    Defaults to ``'flask_session'``.
    """

    SESSION_MONGODB_COLLECT = 'sessions'
    """
    The MongoDB collection you want to use.

    Defaults to ``'sessions'``.
    """

    SESSION_SQLALCHEMY = db
    """
    A :class:`~flask_unchained.bundles.sqlalchemy.SQLAlchemy` extension instance.
    """

    SESSION_SQLALCHEMY_TABLE = 'flask_sessions'
    """
    The name of the SQL table you want to use.

    Defaults to ``flask_sessions``.
    """

    SESSION_SQLALCHEMY_MODEL = None
    """
    Set this if you need to customize the 
    :class:`~flask_unchained.bundles.sqlalchemy.BaseModel` subclass used for
    storing sessions in the database.
    """
