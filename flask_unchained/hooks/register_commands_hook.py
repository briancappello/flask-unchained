import click
import itertools

from typing import *
from warnings import warn

from ..app_factory_hook import AppFactoryHook
from ..bundles import Bundle
from ..flask_unchained import FlaskUnchained


class RegisterCommandsHook(AppFactoryHook):
    """
    Registers commands and command groups from bundles.
    """

    name = 'commands'
    """
    The name of this hook.
    """

    bundle_module_names = ['commands']
    """
    The default module this hook loads from.

    Override by setting the ``commands_module_names`` attribute on your
    bundle class.
    """

    run_after = ['services']
    limit_discovery_to_local_declarations = False

    def run_hook(self,
                 app: FlaskUnchained,
                 bundles: List[Bundle],
                 unchained_config: Optional[Dict[str, Any]] = None,
                 ) -> Dict[str, Union[click.Command, click.Group]]:
        """
        Discover CLI commands and command groups from bundles and register them
        with the app.
        """
        commands = {}
        for bundle in bundles:
            command_groups = self.get_bundle_command_groups(bundle)
            commands.update(inherit_docstrings(command_groups, commands))
            commands.update(self.get_bundle_commands(bundle, command_groups))

        for name, command in commands.items():
            if name in app.cli.commands:
                warn(f'Command name conflict: "{name}" is taken.')
                continue
            app.cli.add_command(command, name)
        return commands

    def get_bundle_commands(self,
                            bundle: Bundle,
                            command_groups: Dict[str, click.Group],
                            ) -> Dict[str, click.Command]:
        # when a command belongs to a group, we don't also want to register the command.
        # therefore we collect all the command names belonging to groups, and use that
        # in our is_click_command type-checking fn below
        group_command_names = set(itertools.chain.from_iterable(
            group.commands.keys() for group in command_groups.values()))

        def is_click_command(obj: Any) -> bool:
            return self.is_click_command(obj) and obj.name not in group_command_names

        commands = {}
        for b in bundle._iter_class_hierarchy():
            for module in self.import_bundle_modules(b):
                new = self._collect_from_package(module, is_click_command)
                commands.update(inherit_docstrings(new, commands))
        return commands

    def get_bundle_command_groups(self, bundle: Bundle) -> Dict[str, click.Group]:
        command_groups = {}
        module_found = False
        for b in bundle._iter_class_hierarchy():
            for module in self.import_bundle_modules(b):
                module_found = True
                command_groups.update(
                    self._collect_from_package(module, self.is_click_group)
                )

        groups = {}
        for name in getattr(bundle, 'command_group_names', [bundle.name]):
            try:
                groups[name] = command_groups[name]
            except KeyError as e:
                if module_found and not bundle.is_single_module:
                    warn(f'WARNING: Found a commands module for the {bundle.name} '
                         f'bundle, but there was no command group named {e.args[0]}'
                         f' in it. Either create one, or customize the bundle\'s '
                         f'`command_group_names` class attribute.')
                continue
        return groups

    def is_click_command(self, obj: Any) -> bool:
        return isinstance(obj, click.Command) and not self.is_click_group(obj)

    def is_click_group(self, obj: Any) -> bool:
        return isinstance(obj, click.Group)


def inherit_docstrings(new, preexisting):
    preexisting_names = set(preexisting.keys()) & set(new.keys())
    for name in preexisting_names:
        if not new[name].__doc__:
            new[name].__doc__ = preexisting[name].__doc__

        if isinstance(new[name], click.Group):
            new[name].commands = inherit_docstrings(new[name].commands,
                                                    preexisting[name].commands)
    return new
