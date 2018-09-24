import pytest

from werkzeug.routing import BuildError

from flask_unchained.bundles.controller import Controller, Resource
from flask_unchained.bundles.controller.utils import (
    controller_name, get_param_tuples, get_last_param_name, join,
    method_name_to_url, url_for, _validate_redirect_url)
from py_meta_utils import deep_getattr


def test_deep_getattr():
    clsdict = {'a': 'clsdict'}

    class First:
        a = 'first'
        b = 'first'

    class Second:
        b = 'second'
        c = 'second'

    bases = (First, Second)

    assert deep_getattr(clsdict, bases, 'a') == 'clsdict'
    assert deep_getattr(clsdict, bases, 'b') == 'first'
    assert deep_getattr(clsdict, bases, 'c') == 'second'
    with pytest.raises(AttributeError):
        deep_getattr(clsdict, bases, 'd')

    assert deep_getattr(clsdict, bases, 'a', 'default') == 'clsdict'
    assert deep_getattr(clsdict, bases, 'b', 'default') == 'first'
    assert deep_getattr(clsdict, bases, 'c', 'default') == 'second'
    assert deep_getattr(clsdict, bases, 'd', 'default') == 'default'


class TestControllerName:
    def test_it_strips_controller(self):
        class UserController(Controller):
            pass
        assert controller_name(UserController) == 'user'

    def test_it_handles_acronyms(self):
        class APIController(Controller):
            pass

        assert controller_name(APIController) == 'api'

    def test_it_strips_view(self):
        class SomeView(Controller):
            pass
        assert controller_name(SomeView) == 'some'

    def test_it_works_with_more_than_one_word(self):
        class MoreThanOneWordController(Controller):
            pass
        assert controller_name(MoreThanOneWordController) == 'more_than_one_word'

    def test_it_strips_resource(self):
        class UserResource(Resource):
            pass
        assert controller_name(UserResource) == 'user'

    def test_it_strips_method_view(self):
        class RoleMethodView(Resource):
            pass
        assert controller_name(RoleMethodView) == 'role'

    def test_it_only_strips_one_suffix(self):
        class RoleViewControllerResource(Resource):
            pass
        assert controller_name(RoleViewControllerResource) == 'role_view_controller'

    def test_it_works_without_stripping_any_suffixes(self):
        class SomeCtrl(Controller):
            pass
        assert controller_name(SomeCtrl) == 'some_ctrl'


class TestGetParamTuples:
    def test_it_works(self):
        assert get_param_tuples('<int:id>') == [('int', 'id')]

    def test_it_works_on_garbage(self):
        assert get_param_tuples(None) == []

    def test_multiple(self):
        path = '/users/<int:user_id>/roles/<string:slug>'
        assert get_param_tuples(path) == [('int', 'user_id'), ('string', 'slug')]


class TestGetLastParamName:
    def test_it_works(self):
        assert get_last_param_name('/foo/<id>') == 'id'
        assert get_last_param_name('/foo/<int:id>') == 'id'

    def test_it_works_on_garbage(self):
        assert get_last_param_name(None) is None

    def test_it_ignores_not_last_params(self):
        assert get_last_param_name('/foo/<int:id>/roles') is None

    def test_it_works_on_deep_parameters(self):
        path = '/foo/<int:id>/bar/<any:something>/baz/<string:bazzes>'
        assert get_last_param_name(path) == 'bazzes'


class TestUrlFor:
    def test_it_works_with_already_formed_path(self):
        assert url_for('/foobar') == '/foobar'

    def test_it_works_with_garbage(self):
        assert url_for(None) is None

    def test_it_works_with_config_keys_returning_path(self, app):
        app.config.from_mapping({'MY_KEY': '/my-key'})
        assert url_for('MY_KEY') == '/my-key'

    def test_it_works_with_config_keys_returning_endpoints(self, app):
        app.config.from_mapping({'MY_KEY': 'some.endpoint'})

        with pytest.raises(BuildError):
            assert url_for('MY_KEY')

        with app.test_request_context():
            app.add_url_rule('/some-endpoint', endpoint='some.endpoint')
            assert url_for('MY_KEY') == '/some-endpoint'

    def test_it_works_with_endpoints(self, app):
        with pytest.raises(BuildError):
            assert url_for('some.endpoint')

        with app.test_request_context():
            app.add_url_rule('/some-endpoint', endpoint='some.endpoint')
            assert url_for('some.endpoint') == '/some-endpoint'

    def test_it_works_with_controller_method_names(self, app):
        class SiteController(Controller):
            def about_us(self):
                pass

        with app.test_request_context():
            app.add_url_rule('/about-us', endpoint='site_controller.about_us')
            assert url_for('about_us', _cls=SiteController) == '/about-us'

    def test_it_works_with_url_for_kwargs(self, app):
        class SiteResource(Resource):
            def get(self, id):
                pass

        with app.test_request_context():
            app.add_url_rule('/sites/<int:id>', endpoint='site_resource.get')
            assert url_for('get', id=1, _cls=SiteResource) == '/sites/1'

            app.add_url_rule('/foo/<string:slug>', endpoint='some.endpoint')
            assert url_for('some.endpoint', slug='hi') == '/foo/hi'

    def test_it_falls_through_if_class_endpoint_not_found(self, app):
        class SiteResource(Resource):
            def get(self, id):
                pass

        with app.test_request_context():
            app.add_url_rule('/sites/<int:id>', endpoint='site_resource.get')
            with pytest.raises(BuildError):
                url_for('delete', id=1, _cls=SiteResource)


class TestJoin:
    def test_it_works_with_garbage(self):
        assert join(None) == '/'
        assert join(None, None, '', 0) == '/'

    def test_it_works_with_partially_valid_input(self):
        assert join('/', 'foo', None, 'bar', '', 'baz') == '/foo/bar/baz'

    def test_it_strips_neighboring_slashes(self):
        assert join('/', '/foo', '/', '/bar') == '/foo/bar'

    def test_it_doesnt_eat_single_slash(self):
        assert join('/', '/') == '/'
        assert join(None, '/') == '/'
        assert join('/', None) == '/'

    def test_it_strips_trailing_slash(self):
        assert join('/foo/bar/') == '/foo/bar'
        assert join('/foo/bar/', None) == '/foo/bar'
        assert join('/foo/bar/', '/') == '/foo/bar'
        assert join('/foo', 'bar/') == '/foo/bar'

    def test_trailing_slash(self):
        assert join('/', trailing_slash=True) == '/'
        assert join('/foo', 'baz', None, trailing_slash=True) == '/foo/baz/'
        assert join('/foo', 'baz/', trailing_slash=True) == '/foo/baz/'


class TestMethodNameToUrl:
    def test_it_works(self):
        assert method_name_to_url('fooBar') == '/foo-bar'
        assert method_name_to_url('foo_bar') == '/foo-bar'
        assert method_name_to_url('fooBar_baz') == '/foo-bar-baz'
        assert method_name_to_url('_FooBar_baz-booFoo_') == '/foo-bar-baz-boo-foo'


class TestValidateRedirectUrl:
    def test_it_fails_on_garbage(self):
        assert _validate_redirect_url(None) is False
        assert _validate_redirect_url(' ') is False

    def test_it_fails_with_invalid_netloc(self, app, monkeypatch):
        with app.test_request_context():
            monkeypatch.setattr('flask.request.host_url', 'http://example.com')
            assert _validate_redirect_url('http://fail.com') is False
            monkeypatch.undo()

    @pytest.mark.options(EXTERNAL_SERVER_NAME='works.com')
    def test_it_works_with_external_server_name(self, app, monkeypatch):
        with app.test_request_context():
            monkeypatch.setattr('flask.request.host_url', 'http://example.com')
            assert _validate_redirect_url('http://works.com') is True
            monkeypatch.undo()

    def test_it_works_with_explicit_external_host(self, app, monkeypatch):
        with app.test_request_context():
            monkeypatch.setattr('flask.request.host_url', 'http://example.com')
            result = _validate_redirect_url('http://works.com',
                                            _external_host='works.com')
            assert result is True
            monkeypatch.undo()
