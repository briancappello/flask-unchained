import pytest

from flask_unchained.decorators import param_converter
from flask_unchained.bundles.sqlalchemy.pytest import ModelFactory
from werkzeug.exceptions import NotFound


@pytest.fixture()
def user(request):
    from ._bundles.vendor_one.models import OneUser

    class UserFactory(ModelFactory):
        class Meta:
            model = OneUser
        name = 'user'

    kwargs = getattr(request.node.get_closest_marker('user'), 'kwargs', {})
    return UserFactory(**kwargs)


@pytest.fixture()
def role(request):
    from ._bundles.vendor_one.models import OneRole

    class RoleFactory(ModelFactory):
        class Meta:
            model = OneRole
        name = 'ROLE_USER'

    kwargs = getattr(request.node.get_closest_marker('role'), 'kwargs', {})
    return RoleFactory(**kwargs)


@pytest.mark.usefixtures('bundles', 'app')
@pytest.mark.bundles(['tests.bundles.sqlalchemy._bundles.vendor_one'])
class TestParamConverter:
    def test_it_works(self, user, role):
        from ._bundles.vendor_one.models import OneUser, OneRole

        @param_converter(id=OneUser, one_role_id=OneRole)
        def method(one_user, one_role):
            assert one_user.id == user.id
            assert one_role.id == role.id

        method(id=user.id, one_role_id=role.id)

    def test_custom_arg_names(self, user, role):
        from ._bundles.vendor_one.models import OneUser, OneRole

        @param_converter(id={'a_user': OneUser}, one_role_id={'a_role': OneRole})
        def method(a_user, a_role):
            assert a_user.id == user.id
            assert a_role.id == role.id

        method(id=user.id, one_role_id=role.id)

    def test_404_on_lookup_error(self, user, role):
        from ._bundles.vendor_one.models import OneUser, OneRole

        @param_converter(id=OneUser, one_role_id=OneRole)
        def method(one_user, one_role):
            assert False

        with pytest.raises(NotFound):
            method(id=0, one_role_id=role.id)

        @param_converter(id=OneUser, one_role_id=OneRole)
        def method(one_user, one_role):
            assert False

        with pytest.raises(NotFound):
            method(id=user.id, one_role_id=0)

    def test_query_param_simple_type_conversion(self, app):
        with app.test_request_context('/?something=42'):
            @param_converter(something=int)
            def method(something):
                assert something == 42
            method()

    def test_query_param_dict_lookup(self, app):
        with app.test_request_context('/?something=foo'):
            @param_converter(something={'foo': 'bar'})
            def method(something):
                assert something == 'bar'
            method()

    def test_query_param_enum_lookup(self, app):
        from enum import Enum

        class FooEnum(Enum):
            Foobar = 'Foobar'

        with app.test_request_context('/?something=Foobar'):
            @param_converter(something=FooEnum)
            def method(something):
                assert something == FooEnum.Foobar
            method()

    def test_query_param_callable_conversion(self, app):
        with app.test_request_context('/?something=2'):
            @param_converter(something=lambda x: int(x) * 2)
            def method(something):
                assert something == 4
            method()

    def test_multiple_query_params(self, app):
        with app.test_request_context('/?foo=42&baz=boo'):
            @param_converter(foo=int, baz=str)
            def method(foo, baz):
                assert foo == 42
                assert baz == 'boo'
            method()

    def test_with_model_and_query_param(self, app, user):
        from ._bundles.vendor_one.models import OneUser

        with app.test_request_context('/?foo=42'):
            @param_converter(id=OneUser, foo=int)
            def method(one_user, foo):
                assert one_user.id == user.id
                assert foo == 42
            method(id=user.id)
