import pytest

from flask_unchained import AppFactory, TEST, unchained


@pytest.fixture()
def bundles(request):
    return getattr(request.keywords.get('bundles'), 'args', [None])[0]


@pytest.fixture()
def app(bundles):
    unchained._reset()
    app = AppFactory.create_app(TEST, bundles=bundles)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()
