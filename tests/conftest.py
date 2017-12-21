import pytest

from flask import Flask
from flask_unchained.unchained_extension import Unchained


unchained = Unchained()


@pytest.fixture()
def app():
    app = Flask('tests')
    unchained.init_app(app, [])
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()
