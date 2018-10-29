import pytest

from flask_unchained.constants import DEV
from flask_unchained.hooks.configure_app_hook import ConfigureAppHook
from flask_unchained.unchained import Unchained

from .._bundles.myapp import MyAppBundle
from .._bundles.empty_bundle import EmptyBundle
from .._bundles.vendor_bundle import VendorBundle


@pytest.fixture
def hook():
    return ConfigureAppHook(Unchained(DEV))


class TestConfigureAppHook:
    def test_later_bundle_configs_override_earlier_ones(self, app,
                                                        hook: ConfigureAppHook):
        hook.run_hook(app, [VendorBundle(), EmptyBundle(), MyAppBundle()])

        assert app.config.APP_KEY == 'app_key'
        assert app.config.VENDOR_KEY1 == 'app_override'
        assert app.config.VENDOR_KEY2 == 'vendor_key2'

    def test_the_app_bundle_config_module_is_named_config(self, hook: ConfigureAppHook):
        assert hook.get_module_name(MyAppBundle()) == 'tests._bundles.myapp.config'
