import functools
from flask import Blueprint

from flask_unchained.bundles.controller import Controller


bp = Blueprint('bp', __name__, url_prefix='/bp')


class DefaultController(Controller):
    pass


def view_func(*args):
    """view_func docstring"""
    return args


def first(fn):
    """first other docstring"""
    def wrapper(*args):
        return fn(*(list(args) + ['first']))
    return wrapper
first.__module__ = 'something.else.first'


def second(fn):
    """second other docstring"""
    def wrapper(*args):
        return fn(*(list(args) + ['second']))
    return wrapper
second.__module__ = 'something.else.second'


def third(fn):
    """third other docstring"""

    # decorators applied directly to class methods (as opposed to listed in
    # the class attribute `decorators`) must use functools.wraps
    # (which correctly implemented decorators should be doing anyway)
    @functools.wraps(fn)
    def wrapper(*args):
        return fn(*(list(args) + ['third']))
    return wrapper
third.__module__ = 'something.else.third'


class TestControllerAttributes:
    def test_auto_attributes(self):
        assert DefaultController.Meta.template_folder_name == 'default'
        assert DefaultController.Meta.template_file_extension is None
        assert DefaultController.Meta.url_prefix is None
        assert DefaultController.Meta.decorators is None

    def test_custom_template_folder(self):
        class FooController(Controller):
            class Meta:
                template_folder_name = 'defaults'

        assert FooController.Meta.url_prefix is None
        assert FooController.Meta.template_folder_name == 'defaults'
        assert FooController.Meta.template_file_extension is None

    def test_custom_template_extension(self):
        class FooController(Controller):
            class Meta:
                template_file_extension = '.html.j2'

        assert FooController.Meta.template_file_extension == '.html.j2'

    def test_custom_url_prefix(self):
        class FooController(Controller):
            class Meta:
                url_prefix = 'foobar'

        assert FooController.Meta.url_prefix == 'foobar'

    def test_apply_decorators(self):
        controller = DefaultController()

        def decorator(fn):
            """some other docstring"""
            def wrapper(*args, **kwargs):
                return fn('decorator')
            return wrapper
        decorator.__module__ = 'something.else'

        new_view = controller.apply_decorators(view_func, [decorator])
        assert new_view() == ('decorator',)
        assert new_view.__name__ == 'view_func'
        assert new_view.__doc__ == 'view_func docstring'
        assert new_view.__module__ == view_func.__module__

    def test_apply_no_decorators(self):
        controller = DefaultController()

        new_view = controller.apply_decorators(view_func, [])
        assert new_view == view_func

    def test_apply_decorators_order(self):
        controller = DefaultController()

        new_view = controller.apply_decorators(view_func, [first, second])
        assert new_view() == ('first', 'second')
        assert new_view.__name__ == 'view_func'
        assert new_view.__doc__ == 'view_func docstring'
        assert new_view.__module__ == view_func.__module__

    def test_get_decorators(self):
        class FooController(Controller):
            class Meta:
                decorators = (first, second)

        controller = FooController()
        assert controller.get_decorators(None) == (first, second)

    def test_dispatch_request(self):
        class FooController(Controller):
            class Meta:
                decorators = (first, second)

            @third
            def my_method(self, *args):
                return args

        controller = FooController()
        resp = controller.dispatch_request('my_method')
        assert resp == ('first', 'second', 'third')

        resp = controller.dispatch_request('my_method', 'a view arg')
        assert resp == ('a view arg', 'first', 'second', 'third',)

    def test_method_as_view(self):
        class FooController(Controller):
            class Meta:
                decorators = (first, second)

            @third
            def my_method(self, *args):
                """my_method docstring"""
                return args

        view = FooController.method_as_view('my_method')
        assert view() == ('first', 'second', 'third')
        assert view.__name__ == 'my_method'
        assert view.__doc__ == 'my_method docstring'
        assert view.__module__ == FooController.__module__

    def test_render(self, app, templates):
        controller = DefaultController()

        resp = controller.render('index', some_ctx_var='hi')

        assert 'DefaultController:index' in resp
        assert templates[0].template.name == 'default/index.html'
        assert templates[0].context.get('some_ctx_var') == 'hi'

    def test_render_with_custom_controller_template_attrs(self, templates):
        class FooController(Controller):
            class Meta:
                template_folder_name = 'foobar'
                template_file_extension = '.html.j2'

        controller = FooController()
        resp = controller.render('index', some_ctx_var='hi')

        assert 'FoobarController:index' in resp
        assert templates[0].template.name == 'foobar/index.html.j2'
        assert templates[0].context.get('some_ctx_var') == 'hi'

    def test_render_with_full_filename(self, templates):
        class FooController(Controller):
            class Meta:
                template_folder_name = 'foobar'

        controller = FooController()
        resp = controller.render('index.html.j2', some_ctx_var='hi')

        assert 'FoobarController:index' in resp
        assert templates[0].template.name == 'foobar/index.html.j2'
        assert templates[0].context.get('some_ctx_var') == 'hi'

    def test_render_with_full_path(self, templates):
        controller = DefaultController()
        resp = controller.render('foobar/index.html.j2', some_ctx_var='hi')

        assert 'FoobarController:index' in resp
        assert templates[0].template.name == 'foobar/index.html.j2'
        assert templates[0].context.get('some_ctx_var') == 'hi'

    def test_default_redirect(self, app):
        controller = DefaultController()

        with app.test_request_context():
            resp = controller.redirect()
            assert resp.status_code == 302
            assert resp.location == '/'

    def test_redirect(self, app):
        controller = DefaultController()

        with app.test_request_context():
            resp = controller.redirect('/path')
            assert resp.status_code == 302
            assert resp.location == '/path'

    def test_redirect_from_config_key(self, app):
        app.config.from_mapping({'MY_CONFIG_KEY': '/path'})
        controller = DefaultController()

        with app.test_request_context():
            resp = controller.redirect('MY_CONFIG_KEY')
            assert resp.status_code == 302
            assert resp.location == '/path'

    def test_redirect_override_from_config_key(self, app):
        app.config.from_mapping({'MY_CONFIG_KEY': '/path'})
        controller = DefaultController()

        with app.test_request_context():
            resp = controller.redirect('/foobar', override='MY_CONFIG_KEY')
            assert resp.status_code == 302
            assert resp.location == '/path'

    def test_redirect_from_query_string(self, app, monkeypatch):
        controller = DefaultController()

        with app.test_request_context():
            monkeypatch.setattr('flask.request.args', {'next': '/path'})
            resp = controller.redirect()
            assert resp.status_code == 302
            assert resp.location == '/path'
            monkeypatch.undo()

    def test_redirect_from_query_string_with_default(self, app, monkeypatch):
        controller = DefaultController()

        with app.test_request_context():
            resp = controller.redirect('/if-not-query-string')
            assert resp.status_code == 302
            assert resp.location == '/if-not-query-string'

            monkeypatch.setattr('flask.request.args', {'next': '/path'})
            resp = controller.redirect('/if-not-query-string')
            assert resp.status_code == 302
            assert resp.location == '/path'
            monkeypatch.undo()

    def test_override_redirect_from_query_string(self, app, monkeypatch):
        controller = DefaultController()

        with app.test_request_context():
            monkeypatch.setattr('flask.request.args', {'next': '/path'})
            resp = controller.redirect(override='/my-path')
            assert resp.status_code == 302
            assert resp.location == '/my-path'
            monkeypatch.undo()

    def test_redirect_with_endpoint(self, app):
        controller = DefaultController()

        with app.test_request_context():
            app.add_url_rule('/endpoint-path', endpoint='my.endpoint')
            resp = controller.redirect('my.endpoint')
            assert resp.status_code == 302
            assert resp.location == '/endpoint-path'

    def test_override_redirect_with_endpoint(self, app):
        controller = DefaultController()

        with app.test_request_context():
            app.add_url_rule('/endpoint-path', endpoint='my.endpoint')
            resp = controller.redirect('/path', override='my.endpoint')
            assert resp.status_code == 302
            assert resp.location == '/endpoint-path'
