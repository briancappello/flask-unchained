import pytest
import sys

from flask_unchained.constants import DEV
from flask_unchained.hooks.register_commands_hook import RegisterCommandsHook
from flask_unchained.unchained import Unchained

from .._bundles.myapp import MyAppBundle
from .._bundles.vendor_bundle import VendorBundle
from .._bundles.override_vendor_bundle import VendorBundle as OverrideVendorBundle


@pytest.fixture()
def hook():
    reset_module('tests._bundles.vendor_bundle.commands')
    reset_module('tests._bundles.override_vendor_bundle.commands')
    reset_module('tests._bundles.myapp.commands')
    return RegisterCommandsHook(Unchained(DEV))


def reset_module(name):
    try:
        del sys.modules[name]
    except KeyError:
        pass


def assert_cmd(cli_runner, cmd, *args, expected=None):
    result = cli_runner.invoke(cmd, args)
    assert result.output.strip() == (expected or ''), cmd.name
    assert result.exit_code == 0, cmd.name


class TestRegisterCommandsHook:
    def test_top_level_command(self, app, hook: RegisterCommandsHook, cli_runner):
        hook.run_hook(app, [VendorBundle(), MyAppBundle()])

        assert 'top_level' in app.cli.commands
        assert_cmd(cli_runner, app.cli.commands['top_level'], expected='myapp')

    def test_app_bundle_overrides_vendor(self, app, hook: RegisterCommandsHook,
                                         cli_runner):
        hook.run_hook(app, [VendorBundle(), MyAppBundle()])

        assert 'vendor_top_level' in app.cli.commands
        vendor_top_level = app.cli.commands['vendor_top_level']
        assert vendor_top_level.__doc__ == 'vendor_bundle docstring'
        assert_cmd(cli_runner, vendor_top_level, expected='vendor_bundle')

        # foo_group
        assert 'foo_group' in app.cli.commands
        foo_group = app.cli.commands['foo_group']
        assert foo_group.__doc__ == 'vendor_bundle docstring'

        assert 'bar' in foo_group.commands
        bar = foo_group.commands['bar']
        assert bar.__doc__ == 'vendor_bundle docstring'
        assert_cmd(cli_runner, bar, expected='vendor_bundle')

        assert 'baz' in foo_group.commands
        baz = foo_group.commands['baz']
        assert baz.__doc__ == 'myapp docstring'
        assert_cmd(cli_runner, baz, expected='myapp')

        # goo_group
        assert 'goo_group' in app.cli.commands
        goo_group = app.cli.commands['goo_group']
        assert goo_group.__doc__ == 'myapp docstring'

        assert 'gar' in goo_group.commands
        gar = goo_group.commands['gar']
        assert gar.__doc__ == 'vendor_bundle docstring'
        assert_cmd(cli_runner, gar, expected='myapp')

        assert 'gaz' not in goo_group.commands

    def test_vendor_bundle_overrides(self, app, hook: RegisterCommandsHook, cli_runner):
        hook.run_hook(app, [OverrideVendorBundle(), MyAppBundle()])

        assert 'vendor_top_level' in app.cli.commands
        vendor_top_level = app.cli.commands['vendor_top_level']
        assert vendor_top_level.__doc__ == 'override_vendor_bundle docstring'
        assert_cmd(cli_runner, vendor_top_level, expected='override_vendor_bundle')

        # foo_group
        assert 'foo_group' in app.cli.commands
        foo_group = app.cli.commands['foo_group']
        assert foo_group.__doc__ == 'vendor_bundle docstring'

        assert 'bar' in foo_group.commands
        bar = foo_group.commands['bar']
        assert bar.__doc__ == 'override_vendor_bundle docstring'
        assert_cmd(cli_runner, bar, expected='override_vendor_bundle')

        assert 'baz' in foo_group.commands
        baz = foo_group.commands['baz']
        assert baz.__doc__ == 'myapp docstring'
        assert_cmd(cli_runner, baz, expected='myapp')

        # goo_group
        assert 'goo_group' in app.cli.commands
        goo_group = app.cli.commands['goo_group']
        assert goo_group.__doc__ == 'myapp docstring'

        assert 'gar' in goo_group.commands
        gar = goo_group.commands['gar']
        assert gar.__doc__ == 'vendor_bundle docstring'
        assert_cmd(cli_runner, gar, expected='myapp')

        assert 'gaz' not in goo_group.commands
