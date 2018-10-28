import importlib
import os
import pytest
import sys

from flask_unchained.bundles.sqlalchemy.pytest import *
from flask_unchained import AppFactory, TEST, unchained
from sqlalchemy import MetaData
from sqlalchemy.orm import clear_mappers


POSTGRES = '{dialect}://{user}:{password}@{host}:{port}/{db_name}'.format(
    dialect=os.getenv('FLASK_DATABASE_ENGINE', 'postgresql+psycopg2'),
    user=os.getenv('FLASK_DATABASE_USER', 'flask_test'),
    password=os.getenv('FLASK_DATABASE_PASSWORD', 'flask_test'),
    host=os.getenv('FLASK_DATABASE_HOST', '127.0.0.1'),
    port=os.getenv('FLASK_DATABASE_PORT', 5432),
    db_name=os.getenv('FLASK_DATABASE_NAME', 'flask_test'))

PRIOR_FLASK_ENV = os.getenv('FLASK_ENV', None)


# reset the Flask-SQLAlchemy extension and the UnchainedModelRegistry to a clean slate,
# support loading the extension from different test bundles.
# NOTE: luckily none of these hacks are required in end users' test suites that
# make use of flask_unchained.bundles.sqlalchemy
@pytest.fixture(autouse=True)
def db_ext(bundles):
    os.environ['FLASK_ENV'] = TEST
    os.environ['SQLA_TESTING'] = 'True'

    sqla_bundle = 'flask_unchained.bundles.sqlalchemy'
    db_bundles = [sqla_bundle, 'tests.bundles.sqlalchemy._bundles.custom_extension']
    try:
        bundle_under_test = [m for m in db_bundles if m in bundles][0]
    except (IndexError, TypeError):
        bundle_under_test = sqla_bundle

    UnchainedModelRegistry()._reset()
    clear_mappers()
    unchained._reset()

    # NOTE: this logic is only correct for one level deep of bundle extension
    # (the proper behavior from unchained hooks is to import the full
    # inheritance hierarchy, and that is especially essential for all of the
    # metaclass magic in this bundle to work correctly)
    modules_to_import = ([bundle_under_test] if bundle_under_test == sqla_bundle
                         else [sqla_bundle, bundle_under_test])

    for module_name in modules_to_import:
        if module_name in sys.modules:
            del sys.modules[module_name]
        db_module = importlib.import_module(module_name)

        ext_module_name = f'{module_name}.extensions'
        if ext_module_name in sys.modules:
            del sys.modules[ext_module_name]
        db_extensions_module = importlib.import_module(ext_module_name)

    kwargs = getattr(db_extensions_module, 'kwargs', dict(
        metadata=MetaData(naming_convention={
            'ix': 'ix_%(column_0_label)s',
            'uq': 'uq_%(table_name)s_%(column_0_name)s',
            'ck': 'ck_%(table_name)s_%(constraint_name)s',
            'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
            'pk': 'pk_%(table_name)s',
        }),
    ))

    db = db_extensions_module.SQLAlchemyUnchained(**kwargs)
    unchained.extensions.db = db

    for module in [db_module, db_extensions_module]:
        setattr(module, 'db', db)

    EXTENSIONS = getattr(db_extensions_module, 'EXTENSIONS')
    EXTENSIONS['db'] = db
    setattr(db_extensions_module, 'EXTENSIONS', EXTENSIONS)

    yield db


@pytest.fixture(autouse=True)
def app(bundles, db_ext, request):
    if (bundles and 'tests.bundles.sqlalchemy._bundles.custom_extension' not in bundles
            and 'flask_unchained.bundles.sqlalchemy' not in bundles):
        bundles.insert(0, 'flask_unchained.bundles.sqlalchemy')

    options = {}
    for mark in request.node.iter_markers('options'):
        kwargs = getattr(mark, 'kwargs', {})
        options.update({k.upper(): v for k, v in kwargs.items()})

    app = AppFactory.create_app(TEST, bundles=bundles, _config_overrides=options)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()

    if PRIOR_FLASK_ENV:
        os.environ['FLASK_ENV'] = PRIOR_FLASK_ENV
    else:
        del os.environ['FLASK_ENV']
    del os.environ['SQLA_TESTING']


@pytest.fixture(autouse=True)
def db(db_ext):
    db_ext.create_all()
    yield db_ext
    db_ext.drop_all()
