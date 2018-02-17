import pytest

from flask import Flask
from flask_unchained import AppConfig
from flask_unchained.unchained import Unchained


unchained = Unchained(AppConfig)


@pytest.fixture()
def app():
    app = Flask('tests')
    unchained.init_app(app)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()
