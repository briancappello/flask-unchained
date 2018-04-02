import importlib
import pytest

from _pytest.fixtures import FixtureLookupError

from .app_factory import AppFactory
from .constants import TEST


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
def app():
    app = AppFactory.create_app(TEST)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


@pytest.fixture(autouse=True)
def maybe_inject_extensions_and_services(app, request):
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
