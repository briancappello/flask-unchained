import click
import inspect

from flask import Flask
from ..app_factory_hook import AppFactoryHook
from ..bundle import Bundle
from typing import List
from warnings import warn


class RegisterCommandsHook(AppFactoryHook):
    """Adds commands and command groups from bundles."""
    bundle_module_name = 'commands'
    name = 'commands'
    priority = 95

    def run_hook(self, app: Flask, bundles: List[Bundle]):
        commands = []
        for bundle in bundles:
            bundle_command_groups = self.get_bundle_command_groups(bundle)
            commands += bundle_command_groups
            commands += self.get_bundle_commands(bundle, bundle_command_groups)

        for name, command in commands:
            if name in app.cli.commands:
                warn(f'Command name conflict: "{name}" is taken.')
                continue
            app.cli.add_command(command, name)

    def get_bundle_commands(self, bundle: Bundle, bundle_command_groups):
        commands_module = self.import_bundle_module(bundle)
        if not commands_module:
            return []

        group_commands = {}
        for _, group in bundle_command_groups:
            group_commands.update(group.commands)

        def is_click_command(obj):
            return self.is_click_command(obj) and obj.name not in group_commands

        return [(command.name, command) for _, command in
                inspect.getmembers(commands_module, is_click_command)]

    def get_bundle_command_groups(self, bundle: Bundle):
        commands_module = self.import_bundle_module(bundle)
        if not commands_module:
            return []

        command_groups = dict(inspect.getmembers(commands_module,
                                                 self.is_click_group))
        tuples = []
        for name in getattr(bundle, 'command_group_names', [bundle.name]):
            try:
                command_group = command_groups[name]
            except KeyError as e:
                warn(f'WARNING: Found a commands module for the {bundle.name} '
                     f'bundle, but there was no command group named {e.args[0]}'
                     f' in it. Either create one, or customize the bundle\'s '
                     f'`command_group_names` class attribute.')
                continue
            tuples.append((name, command_group))
        return tuples

    def is_click_command(self, obj) -> bool:
        return isinstance(obj, click.Command) and not self.is_click_group(obj)

    def is_click_group(self, obj) -> bool:
        return isinstance(obj, click.Group)
