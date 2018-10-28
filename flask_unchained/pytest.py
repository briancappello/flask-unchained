import importlib
import inspect
import json
import pytest

from click.testing import CliRunner
from collections import namedtuple
from flask import Response, template_rendered
from flask.cli import ScriptInfo
from flask.testing import FlaskClient
from flask_unchained import url_for
from urllib.parse import urlparse
from werkzeug.test import EnvironBuilder
from werkzeug.utils import cached_property
from _pytest.fixtures import FixtureLookupError

from .app_factory import AppFactory
from .constants import TEST
from .unchained import unchained


RenderedTemplate = namedtuple('RenderedTemplate', 'template context')
"""
A ``namedtuple`` returned by the :func:`~flask_unchained.pytest.templates` fixture.
"""

ENV_BUILDER_KWARGS = {name for name, param
                      in inspect.signature(EnvironBuilder).parameters.items()
                      if (param.kind == param.POSITIONAL_OR_KEYWORD
                          or param.kind == param.KEYWORD_ONLY)}


def optional_pytest_fixture(required_module_name, scope='function', params=None,
                            autouse=False, ids=None, name=None):
    def wrapper(fn):
        try:
            importlib.import_module(required_module_name)
        except (ImportError, ModuleNotFoundError):
            return pytest.fixture(name=name or fn.__name__)(lambda: None)
        return pytest.fixture(scope, params, autouse, ids, name)(fn)
    return wrapper


@pytest.fixture(autouse=True, scope='session')
def app(request):
    """
    Automatically used test fixture. Returns the application instance-under-test with
    a valid app context.
    """
    unchained._reset()

    options = {}
    for mark in request.node.iter_markers('options'):
        kwargs = getattr(mark, 'kwargs', {})
        options.update({k.upper(): v for k, v in kwargs.items()})

    app = AppFactory.create_app(TEST, _config_overrides=options)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


# FIXME this only seems to work on tests themselves, but *not* for test fixtures :(
@pytest.fixture(autouse=True)
def maybe_inject_extensions_and_services(app, request):
    """
    Automatically used test fixture. Allows for using services and extensions as
    if they were test fixtures::

        def test_something(db, mail, security_service, user_manager):
            # assert important stuff

    **NOTE:** This only works on tests themselves; it will *not* work on test fixtures
    """
    item = request._pyfuncitem
    fixture_names = getattr(item, "fixturenames", request.fixturenames)
    for arg_name in fixture_names:
        if arg_name in item.funcargs:
            continue

        try:
            request.getfixturevalue(arg_name)
        except FixtureLookupError:
            if arg_name in app.unchained.extensions:
                item.funcargs[arg_name] = app.unchained.extensions[arg_name]
            elif arg_name in app.unchained.services:
                item.funcargs[arg_name] = app.unchained.services[arg_name]


class FlaskCliRunner(CliRunner):
    """
    Extended from upstream to run commands within the Flask app context.

    The CLI runner provides functionality to invoke a Click command line
    script for unit testing purposes in a isolated environment. This only
    works in single-threaded systems without any concurrency as it changes the
    global interpreter state.

    :param charset: the character set for the input and output data.  This is
                    UTF-8 by default and should not be changed currently as
                    the reporting to Click only works in Python 2 properly.
    :param env: a dictionary with environment variables for overriding.
    :param echo_stdin: if this is set to `True`, then reading from stdin writes
                       to stdout.  This is useful for showing examples in
                       some circumstances.  Note that regular prompts
                       will automatically echo the input.
    """
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

    def invoke(self, cli=None, args=None, **kwargs):
        """
        Invokes a command in an isolated environment.  The arguments are
        forwarded directly to the command line script, the `extra` keyword
        arguments are passed to the :meth:`~clickpkg.Command.main` function of
        the command.

        This returns a :class:`~click.testing.Result` object.

        :param cli: the command to invoke
        :param args: the arguments to invoke
        :param input: the input data for `sys.stdin`.
        :param env: the environment overrides.
        :param catch_exceptions: Whether to catch any other exceptions than
                                 ``SystemExit``.
        :param extra: the keyword arguments to pass to :meth:`main`.
        :param color: whether the output should contain color codes. The
                      application can still override this explicitly.
        """
        if cli is None:
            cli = self.app.cli
        if 'obj' not in kwargs:
            kwargs['obj'] = ScriptInfo(create_app=lambda _: self.app)
        return super().invoke(cli, args, **kwargs)


@pytest.fixture()
def cli_runner(app):
    """
    Yields an instance of :class:`FlaskCliRunner`. Example usage::

        from your_package.commands import some_command

        def test_some_command(cli_runner):
            result = cli_runner.invoke(some_command)
            assert result.exit_code == 0
            assert result.output.strip() == 'output of some_command'
    """
    yield FlaskCliRunner(app)


def _process_test_client_args(args, kwargs):
    """
    allow calling client.get, client.post, etc methods with an endpoint name.
    this function forwards the correct kwargs to url_for (as long as they don't
    conflict with the kwarg names of werkzeug.test.EnvironBuilder, in which case
    it would be necessary to use `url_for` in the same way as with FlaskClient)
    """
    endpoint_or_url_or_config_key = args and args[0]
    url_for_kwargs = {}
    for kwarg_name in (set(kwargs) - ENV_BUILDER_KWARGS):
        url_for_kwargs[kwarg_name] = kwargs.pop(kwarg_name)
    url = url_for(endpoint_or_url_or_config_key, **url_for_kwargs)
    return (url, *args[1:]), kwargs


class HtmlTestClient(FlaskClient):
    """
    Like :class:`~flask.testing.FlaskClient`, except it supports passing an endpoint
    as the first argument directly to the HTTP get/post/etc methods (no need to use
    ``url_for``, unless your URL rule has parameter names that conflict with the
    keyword arguments of :class:`~werkzeug.test.EnvironBuilder`). It also adds support
    for following redirects. Example usage::

        def test_something(client: HtmlTestClient):
            r = client.get('site_controller.index')
            assert r.status_code == 200
    """
    def open(self, *args, **kwargs):
        args, kwargs = _process_test_client_args(args, kwargs)
        return super().open(*args, **kwargs)

    def follow_redirects(self, response):
        """
        Follow redirects on a response after inspecting it. Example usage::

            def test_some_view(client):
                r = client.post('some.endpoint.that.redircts', data=data)
                assert r.status_code == 302
                assert r.path == url_for('some.endpoint')

                r = client.follow_redirects(r)
                assert r.status_code == 200
        """
        return super().open(response.location, follow_redirects=True)


class ApiTestClient(HtmlTestClient):
    """
    Like :class:`HtmlTestClient` except it supports automatic serialization to json
    of data, as well as setting the ``Accept`` and ``Content-Type`` headers to
    ``application/json``.
    """
    def open(self, *args, **kwargs):
        kwargs['data'] = json.dumps(kwargs.get('data'))

        kwargs.setdefault('headers', {})
        kwargs['headers']['Content-Type'] = 'application/json'
        kwargs['headers']['Accept'] = 'application/json'

        return super().open(*args, **kwargs)


class HtmlTestResponse(Response):
    """
    Like :class:`flask.wrappers.Response`, except extended with methods for inspecting
    the parsed URL and automatically decoding the response to a string.
    """

    @cached_property
    def _loc(self):
        return urlparse(self.location)

    @cached_property
    def scheme(self):
        """
        Returns the URL scheme specifier of the response's url, eg http or https.
        """
        return self._loc.scheme

    @cached_property
    def netloc(self):
        """
        Returns the network location part the response's url.
        """
        return self._loc.netloc

    @cached_property
    def path(self):
        """
        Returns the path part of the response's url.
        """
        return self._loc.path

    @cached_property
    def params(self):
        """
        Returns the parameters for the last path element in the response's url.
        """
        return self._loc.params

    @cached_property
    def query(self):
        """
        Returns the query component from the response's url.
        """
        return self._loc.query

    @cached_property
    def fragment(self):
        """
        Returns the fragment identifier from the response's url.
        """
        return self._loc.fragment

    @cached_property
    def html(self):
        """
        Returns the response's data parsed to a string of html.
        """
        return self.data.decode('utf-8')


class ApiTestResponse(HtmlTestResponse):
    """
    Like :class:`HtmlTestResponse` except it adds methods for automatically parsing
    the response data as json and retrieving errors from the response data.
    """

    @cached_property
    def json(self):
        """
        Returns the response's data parsed from json.
        """
        assert self.mimetype == 'application/json', (self.mimetype, self.data)
        return json.loads(self.data)

    @cached_property
    def errors(self):
        """
        If the response contains the key ``errors``, return its value, otherwise
        returns an empty dictionary.
        """
        return self.json.get('errors', {})


@pytest.fixture()
def client(app):
    """
    Yields an instance of :class:`HtmlTestClient`. Example usage::

        def test_some_view(client):
            r = client.get('some.endpoint')

            # r is an instance of :class:`HtmlTestResponse`
            assert r.status_code == 200
            assert 'The Page Title' in r.html
    """
    app.test_client_class = HtmlTestClient
    app.response_class = HtmlTestResponse
    with app.test_client() as client:
        yield client


@pytest.fixture()
def api_client(app):
    """
    Yields an instance of :class:`ApiTestClient`. Example usage::

        def test_some_view(api_client):
            r = api_client.get('some.endpoint.returning.json')

            # r is an instance of :class:`ApiTestResponse`
            assert r.status_code == 200
            assert 'some_key' in r.json
    """
    app.test_client_class = ApiTestClient
    app.response_class = ApiTestResponse
    with app.test_client() as client:
        yield client


@pytest.fixture()
def templates(app):
    """
    Fixture to record which templates (if any) got rendered during a request.
    Example Usage::

        def test_some_view(client, templates):
            r = client.get('some.endpoint')
            assert r.status_code == 200
            assert templates[0].template.name == 'some/template.html'
            assert templates[0].context.get('some_ctx_var') == 'expected value'
    """
    records = []

    def record(sender, template, context, **extra):
        records.append(RenderedTemplate(template, context))
    template_rendered.connect(record, app)

    try:
        yield records
    finally:
        template_rendered.disconnect(record, app)
