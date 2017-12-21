import pytest

from flask import Flask


@pytest.fixture()
def app():
    app = Flask('tests')
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()
