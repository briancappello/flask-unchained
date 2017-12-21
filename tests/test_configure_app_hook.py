import pytest

from flask_unchained import AppConfig
from flask_unchained.hooks import ConfigureAppHook
from flask_unchained.unchained_extension import UnchainedStore

from .fixtures.myapp import AppBundle
from .fixtures.empty_bundle import EmptyBundle
from .fixtures.vendor_bundle import VendorBundle


class DevConfig(AppConfig):
    pass


@pytest.fixture
def hook():
    return ConfigureAppHook(UnchainedStore(DevConfig))


class TestConfigureAppHook:
    def test_later_bundle_configs_override_earlier_ones(self, app, hook):
        hook.run_hook(app, [VendorBundle, EmptyBundle, AppBundle])

        assert app.config.get('APP_KEY') == 'app_key'
        assert app.config.get('VENDOR_KEY1') == 'app_override'
        assert app.config.get('VENDOR_KEY2') == 'vendor_key2'

    def test_the_app_bundle_config_module_is_named_config(self, hook):
        assert hook.get_module_name(AppBundle) == 'tests.fixtures.myapp.config'
