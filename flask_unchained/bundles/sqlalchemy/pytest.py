import factory
import pytest

from flask_unchained import unchained, injectable

# must import the model registry here so the right one gets used
from .model_registry import UnchainedModelRegistry


@pytest.fixture(autouse=True, scope='session')
def db(app):
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


class ModelFactory(factory.Factory):
    class Meta:
        abstract = True

    @classmethod
    @unchained.inject('session_manager')
    def _create(cls, model_class, session_manager=injectable, *args, **kwargs):
        # make sure we get the correct mapped class
        model_class = unchained.sqlalchemy_bundle.models[model_class.__name__]

        # try to query for existing by primary key or unique column(s)
        filter_kwargs = {}
        for col in model_class.__mapper__.columns:
            if col.name in kwargs and (col.primary_key or col.unique):
                filter_kwargs[col.name] = kwargs[col.name]

        # otherwise try by all simple type values
        if not filter_kwargs:
            filter_kwargs = {k: v for k, v in kwargs.items()
                             if '__' not in k
                             and (v is None
                                  or isinstance(v, (bool, int, str, float)))}

        instance = (model_class.query.filter_by(**filter_kwargs).one_or_none()
                    if filter_kwargs else None)

        if not instance:
            instance = model_class(*args, **kwargs)
            session_manager.save(instance, commit=True)
        return instance
