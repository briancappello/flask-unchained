import pytest

from flask_unchained import AppFactory, TEST, unchained


@pytest.fixture()
def bundles(request):
    """
    Fixture that allows marking tests as using a specific list of bundles:

        @pytest.mark.bundles(['tests._bundles.one', 'tests._bundles.two'])
        def test_something():
            pass
    """
    try:
        return request.node.get_closest_marker("bundles").args[0]
    except AttributeError:
        from ._unchained_config import BUNDLES

        return BUNDLES


@pytest.fixture(autouse=True)
def app(request, bundles):
    """
    Automatically used test fixture. Returns the application instance-under-test with
    a valid app context.
    """
    unchained._reset()

    options = {}
    for mark in request.node.iter_markers("options"):
        kwargs = getattr(mark, "kwargs", {})
        options.update({k.upper(): v for k, v in kwargs.items()})

    app = AppFactory().create_app(TEST, bundles=bundles, _config_overrides=options)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()
