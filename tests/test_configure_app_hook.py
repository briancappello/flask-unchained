from flask_unchained import AppConfig
from flask_unchained.hooks import ConfigureAppHook

from .fixtures.app_bundle import AppBundle
from .fixtures.empty_bundle import EmptyBundle
from .fixtures.vendor_bundle import VendorBundle


hook = ConfigureAppHook()


def test_configure_app_hook(app):
    class DevConfig(AppConfig):
        pass

    hook.run_hook(app, DevConfig, [VendorBundle, EmptyBundle, AppBundle])

    assert app.config.get('APP_KEY') == 'app_key'
    assert app.config.get('VENDOR_KEY1') == 'app_override'
    assert app.config.get('VENDOR_KEY2') == 'vendor_key2'
