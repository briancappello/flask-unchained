import factory
import pytest

from datetime import datetime, timezone

from flask_unchained import AppFactory, TEST
from flask_unchained.bundles.sqlalchemy.pytest import *
from flask_unchained.bundles.security.pytest import *

from tests.bundles.security._bundles.security.models import User, Role, UserRole


# we need to override the `app` and `db` fixtures to make them function-scoped
# so that the only_if rules on routes work correctly with our @pytest.mark.options

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
    app = AppFactory.create_app(TEST, bundles=bundles + [
        'flask_unchained.bundles.api',
        'flask_unchained.bundles.mail',
        'tests.bundles.security._bundles.security',
        'tests.bundles.security._app',
    ], _config_overrides=options)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


@pytest.fixture(autouse=True)
def db(app):
    db_ext = app.unchained.extensions.db
    # FIXME might need to reflect the current db, drop, and then create...
    db_ext.create_all()
    yield db_ext
    db_ext.drop_all()


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
