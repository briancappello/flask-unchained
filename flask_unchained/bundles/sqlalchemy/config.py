import os

from flask_unchained import BundleConfig

from .alembic.migrations import render_migration_item


class Config(BundleConfig):
    """
    The default configuration options for the SQLAlchemy Bundle.
    """

    db_file = os.path.join(BundleConfig.current_app.root_path or '', 'db',
                           f'{BundleConfig.current_app.env or "development"}.sqlite')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_file}'
    """
    The database URI that should be used for the connection. Defaults to using SQLite
    with the database file stored at ``ROOT_PATH/db/<env>.sqlite``. See the
    `SQLAlchemy Dialects documentation <https://docs.sqlalchemy.org/en/latest/dialects/>`_
    for more info.
    """

    SQLALCHEMY_TRANSACTION_ISOLATION_LEVEL = None
    """
    Set the engine-wide transaction isolation level.

    See `the docs <https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#setting-transaction-isolation-levels>`_
    for more info.
    """

    SQLALCHEMY_ECHO = False
    """
    If set to ``True`` SQLAlchemy will log all the statements issued to stderr which can
    be useful for debugging.
    """

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """
    If set to ``True``, Flask-SQLAlchemy will track modifications of objects and emit
    signals. The default is ``False``. This requires extra memory and should be
    disabled if not needed.
    """

    SQLALCHEMY_RECORD_QUERIES = None
    """
    Can be used to explicitly disable or enable query recording. Query recording
    automatically happens in debug or testing mode. See
    :func:`~flask_sqlalchemy.get_debug_queries` for more information.
    """

    SQLALCHEMY_BINDS = None
    """
    A dictionary that maps bind keys to SQLAlchemy connection URIs.
    """

    SQLALCHEMY_NATIVE_UNICODE = None
    """
    Can be used to explicitly disable native unicode support. This is required for some
    database adapters (like PostgreSQL on some Ubuntu versions) when used with improper
    database defaults that specify encoding-less databases.
    """

    SQLALCHEMY_POOL_SIZE = None
    """
    The size of the database pool. Defaults to the engine’s default (usually 5).
    """

    SQLALCHEMY_POOL_TIMEOUT = None
    """
    Specifies the connection timeout in seconds for the pool.
    """

    SQLALCHEMY_POOL_RECYCLE = None
    """
    Number of seconds after which a connection is automatically recycled. This is
    required for MySQL, which removes connections after 8 hours idle by default.
    Note that Flask-SQLAlchemy automatically sets this to 2 hours if MySQL is used.

    Certain database backends may impose different inactive connection timeouts, which
    interferes with Flask-SQLAlchemy’s connection pooling.

    By default, MariaDB is configured to have a 600 second timeout. This often surfaces
    hard to debug, production environment only exceptions like ``2013: Lost connection to
    MySQL server`` during query.

    If you are using a backend (or a pre-configured database-as-a-service) with a lower
    connection timeout, it is recommended that you set :attr:`SQLALCHEMY_POOL_RECYCLE`
    to a value less than your backend’s timeout.
    """

    SQLALCHEMY_MAX_OVERFLOW = None
    """
    Controls the number of connections that can be created after the pool reached its
    maximum size. When those additional connections are returned to the pool, they are
    disconnected and discarded.
    """

    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    """
    Whether or not to automatically commit on app context teardown. Defaults to False.
    """

    ALEMBIC = {
        'script_location': 'db/migrations',
    }
    """
    Used to set the directory where migrations are stored. `ALEMBIC` should be set to
    a dictionary, using the key `script_location` to set the directory. Defaults to
    ``ROOT_PATH/db/migrations``.
    """

    ALEMBIC_CONTEXT = {
        'render_item': render_migration_item,
        'template_args': {'migration_variables': []},
    }
    """
    Extra kwargs to pass to the constructor of the Flask-Migrate extension. If you
    need to change this, make sure to merge the defaults with your settings!
    """


class TestConfig(Config):
    """
    Default configuration options for testing.
    """

    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # :memory:
    """
    The database URI to use for testing. Defaults to SQLite in memory.
    """
