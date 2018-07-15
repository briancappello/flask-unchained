import inspect
import pytest

from collections import namedtuple
from flask import Response, template_rendered
from flask.testing import FlaskClient
from urllib.parse import urlparse
from werkzeug.test import EnvironBuilder
from werkzeug.utils import cached_property

from .utils import url_for


ENV_BUILDER_KWARGS = {name for name, param
                      in inspect.signature(EnvironBuilder).parameters.items()
                      if (param.kind == param.POSITIONAL_OR_KEYWORD
                          or param.kind == param.KEYWORD_ONLY)}


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
    def open(self, *args, **kwargs):
        args, kwargs = _process_test_client_args(args, kwargs)
        return super().open(*args, **kwargs)

    def follow_redirects(self, response):
        return super().open(response.location, follow_redirects=True)


class HtmlTestResponse(Response):
    @cached_property
    def _loc(self):
        return urlparse(self.location)

    @cached_property
    def scheme(self):
        return self._loc.scheme

    @cached_property
    def netloc(self):
        return self._loc.netloc

    @cached_property
    def path(self):
        return self._loc.path or '/'

    @cached_property
    def params(self):
        return self._loc.params

    @cached_property
    def query(self):
        return self._loc.query

    @cached_property
    def fragment(self):
        return self._loc.fragment

    @cached_property
    def html(self):
        return self.data.decode('utf-8')


@pytest.fixture()
def client(app):
    app.test_client_class = HtmlTestClient
    app.response_class = HtmlTestResponse
    with app.test_client() as client:
        yield client


@pytest.fixture()
def templates(app):
    records = []
    RenderedTemplate = namedtuple('RenderedTemplate', 'template context')

    def record(sender, template, context, **extra):
        records.append(RenderedTemplate(template, context))
    template_rendered.connect(record, app)

    try:
        yield records
    finally:
        template_rendered.disconnect(record, app)
