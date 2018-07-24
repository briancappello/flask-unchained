import json
import pytest

from flask_unchained.pytest import HtmlTestClient, HtmlTestResponse
from werkzeug.utils import cached_property


class ApiTestClient(HtmlTestClient):
    def open(self, *args, **kwargs):
        kwargs['data'] = json.dumps(kwargs.get('data'))

        kwargs.setdefault('headers', {})
        kwargs['headers']['Content-Type'] = 'application/json'
        kwargs['headers']['Accept'] = 'application/json'

        return super().open(*args, **kwargs)


class ApiTestResponse(HtmlTestResponse):
    @cached_property
    def json(self):
        assert self.mimetype == 'application/json', (self.mimetype, self.data)
        return json.loads(self.data)

    @cached_property
    def errors(self):
        return self.json.get('errors', {})


@pytest.fixture()
def api_client(app):
    app.test_client_class = ApiTestClient
    app.response_class = ApiTestResponse
    with app.test_client() as client:
        yield client
