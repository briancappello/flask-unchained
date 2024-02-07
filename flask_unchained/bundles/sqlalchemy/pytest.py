import pytest

from .model_registry import UnchainedModelRegistry  # required import


@pytest.fixture(autouse=True, scope="session")
def db(app):
    # FIXME definitely need to create test database if it doesn't exist
    db_ext = app.unchained.extensions.db
    # FIXME might need to reflect the current db, drop, and then create...
    db_ext.create_all()
    yield db_ext
    db_ext.drop_all()


@pytest.fixture(autouse=True)
def db_session(db):
    connection = db.engine.connect()
    transaction = connection.begin()
    session = db.create_scoped_session(options=dict(bind=connection, binds={}))
    db.session = session

    try:
        yield session
    finally:
        transaction.rollback()
        connection.close()
        session.remove()
