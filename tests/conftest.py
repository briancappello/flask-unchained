import pytest

from flask import Flask
from flask_unchained import AppConfig
from flask_unchained.unchained_extension import UnchainedExtension


unchained = UnchainedExtension()


@pytest.fixture()
def app():
    app = Flask('tests')
    unchained.init_app(app, AppConfig, [])
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()
