import factory
import os

from datetime import datetime, timezone
from flask_unchained.bundles.security.pytest import *
from flask_unchained.bundles.sqlalchemy.model_registry import UnchainedModelRegistry
from flask_unchained.bundles.sqlalchemy.pytest import ModelFactory
from flask_unchained import AppFactory, TEST, unchained

from tests.bundles.security._bundles.security.models import User, Role, UserRole


POSTGRES = '{dialect}://{user}:{password}@{host}:{port}/{db_name}'.format(
    dialect=os.getenv('FLASK_DATABASE_ENGINE', 'postgresql+psycopg2'),
    user=os.getenv('FLASK_DATABASE_USER', 'flask_test'),
    password=os.getenv('FLASK_DATABASE_PASSWORD', 'flask_test'),
    host=os.getenv('FLASK_DATABASE_HOST', '127.0.0.1'),
    port=os.getenv('FLASK_DATABASE_PORT', 5432),
    db_name=os.getenv('FLASK_DATABASE_NAME', 'flask_test'))


@pytest.fixture()
def bundles(request):
    try:
        return request.keywords.get('bundles').args[0]
    except AttributeError:
        from ._unchained_config import BUNDLES
        return BUNDLES


@pytest.fixture(autouse=True)
def app(request, bundles):
    """
    Automatically used test fixture. Returns the application instance-under-test with
    a valid app context.
    """
    unchained._reset()
    options = request.keywords.get('options', None)
    if options is not None:
        options = {k.upper(): v for k, v in options.kwargs.items()}
    app = AppFactory.create_app(TEST, bundles=bundles, _config_overrides=options)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


@pytest.fixture(autouse=True)
def db(app):
    db_ext = app.unchained.extensions.get('db', None)
    if db_ext:
        # FIXME might need to reflect the current db, drop, and then create...
        db_ext.create_all()
        yield db_ext
        db_ext.drop_all()
    else:
        yield None


@pytest.fixture(autouse=True)
def db_session(db):
    if not db:
        yield None
    else:
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


class UserFactory(ModelFactory):
    class Meta:
        model = User

    username = 'user'
    email = 'user@example.com'
    password = 'password'
    first_name = 'first'
    last_name = 'last'
    active = True
    confirmed_at = datetime.now(timezone.utc)


class RoleFactory(ModelFactory):
    class Meta:
        model = Role

    name = 'ROLE_USER'


class UserRoleFactory(ModelFactory):
    class Meta:
        model = UserRole

    user = factory.SubFactory(UserFactory)
    role = factory.SubFactory(RoleFactory)


class UserWithRoleFactory(UserFactory):
    user_role = factory.RelatedFactory(UserRoleFactory, 'user')


class UserWithTwoRolesFactory(UserFactory):
    _user_role = factory.RelatedFactory(UserRoleFactory, 'user',
                                        role__name='ROLE_USER')
    user_role = factory.RelatedFactory(UserRoleFactory, 'user',
                                       role__name='ROLE_USER1')


@pytest.fixture()
def user(request):
    kwargs = getattr(request.keywords.get('user'), 'kwargs', {})
    return UserWithTwoRolesFactory(**kwargs)


@pytest.fixture()
def users(request):
    users_request = request.keywords.get('users')
    if not users_request:
        return

    rv = []
    for kwargs in users_request.args:
        rv.append(UserWithTwoRolesFactory(**kwargs))
    return rv


@pytest.fixture()
def role(request):
    kwargs = getattr(request.keywords.get('role'), 'kwargs', {})
    return RoleFactory(**kwargs)


@pytest.fixture()
def roles(request):
    roles_request = request.keywords.get('roles')
    if not roles_request:
        return

    rv = []
    for kwargs in roles_request.args:
        rv.append(RoleFactory(**kwargs))
    return rv


@pytest.fixture()
def admin(request):
    kwargs = getattr(request.keywords.get('admin'), 'kwargs', {})
    kwargs = dict(**kwargs, username='admin', email='admin@example.com',
                  _user_role__role__name='ROLE_ADMIN')
    kwargs.setdefault('user_role__role__name', 'ROLE_USER')
    return UserWithTwoRolesFactory(**kwargs)
