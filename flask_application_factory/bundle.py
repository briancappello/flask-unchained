import os
import sys

from flask import Flask
from typing import List, Optional
from warnings import warn

from .tuples import (
    AdminTuple,
    BlueprintTuple,
    CommandTuple,
    CommandGroupTuple,
    ExtensionTuple,
    ModelTuple,
    SerializerTuple,
)
from .type_checker import TypeChecker
from .utils import (
    get_members,
    safe_import_module,
    title_case,
)

EXTENSIONS = 'EXTENSIONS'
DEFERRED_EXTENSIONS = 'DEFERRED_EXTENSIONS'
sentinel = object()


class Bundle(object):
    """
    A helper class for auto-registering a group of commands, views, models,
    serializers and admins with the app.

    Bundles are organized just as standard Python modules. If you want to
    customize any of the default names, you can do so in the constructor.

    Each bundle's modules are auto-detected if they exist, and will be
    registered if so. All are optional.

    Simple bundle example::

        $ tree
        backend/
        └── simple/
            ├── __init__.py
            ├── admins.py
            ├── commands.py
            ├── models.py
            ├── serializers.py
            └── views.py

    Big bundle example::

        $ tree
        backend/
        └── big/
            ├── __init__.py
            ├── admins
            │   ├── __init__.py  # must import all ModelAdmin(s)
            │   ├── one_admin.py
            │   └── two_admin.py
            ├── commands
            │   ├── __init__.py  # must import the click group from .group and
            │   │                # all commands
            │   ├── group.py     # the group should have the same name as the
            │   │                # bundle's folder, or to change it, pass
            │   │                # the command_group_names kwarg to Bundle
            │   ├── one.py
            │   └── two.py
            ├── models
            │   ├── __init__.py  # must import all Model(s)
            │   ├── one.py
            │   └── two.py
            ├── serializers
            │   ├── __init__.py  # must import all ModelSerializer(s)
            │   ├── one_serializer.py
            │   └── two_serializer.py
            └── views
                ├── __init__.py  # must import the Blueprint(s) from .blueprint
                │                # and all ModelResource(s)
                ├── blueprint.py # the blueprint should have the same name as the
                │                # bundle's folder, or to change it, pass the
                │                # blueprint_names kwarg to Bundle
                ├── one_resource.py
                └── two_resource.py

    In both cases, :file:`backend/<bundle_folder_name>/__init__.py` is the same::

        $ cat backend/<bundle_folder_name>/__init__.py
        from backend.magic import Bundle

        bundle = Bundle(__name__)

    Finally, the bundle modules must be registered in :file:`backend/config.py`::

        BUNDLES = [
            'backend.simple',
            'backend.big',
        ]
    """
    module_name = ''  # type: str
    """Top-level module name of the bundle (dot notation)"""

    admin_category_name = None  # type: Optional[str]
    """Label to use for the bundle in the admin"""

    admin_icon_class = None  # type: Optional[str]
    """Icon class to use for the bundle in the admin"""

    admins_module_name = 'admins'  # type: Optional[str]
    """module name of the admins in the bundle"""

    bundle_config_module_name = 'bundle_config'
    """module name of the bundle_config in the bundle"""

    commands_module_name = 'commands'  # type: Optional[str]
    """module name of the commands in the bundle"""

    command_group_names = sentinel  # type: Optional[List[str]]
    """List of the bundle's command group names. Defaults to [<bundle_folder_name>]"""

    extensions_module_name = 'extensions'  # type: Optional[str]
    """module name of the extensions in the bundle"""

    models_module_name = 'models'  # type: Optional[str]
    """module name of the models in the bundle"""

    serializers_module_name = 'serializers'  # type: Optional[str]
    """module name of the serializers in the bundle"""

    views_module_name = 'views'  # type: Optional[str]
    """module name of the views in the bundle"""

    blueprint_names = sentinel  # type: Optional[List[str]]
    """List of Blueprint name(s) to register. Defaults to [<bundle_folder_name>] (**NOTE**: names of the *instance variables*, not the Blueprints' endpoint names.)"""

    type_checker = TypeChecker()  # type: TypeChecker

    def __init__(self):
        if self.module_name.endswith('.bundle'):
            self.module_name = self.module_name[:-len('.bundle')]
        self.root_dir = os.path.dirname(sys.modules[self.module_name].__file__)

    def pre_configure_app(self, app: Flask, app_config, bundles: list):
        bundle_config = self.get_bundle_config(app_config.__name__)
        if bundle_config:
            app.config.from_object(bundle_config)

    def post_configure_app(self, app: Flask, bundles: list):
        pass

    def post_register_extensions(self, app: Flask, bundles: list):
        pass

    def pre_register_deferred_extensions(self, app: Flask, bundles: list):
        pass

    def post_register_deferred_extensions(self, app: Flask, bundles: list):
        pass

    def finalize_app(self, app: Flask, bundles: list):
        pass

    @property
    def name(self) -> str:
        if '.' not in self.module_name:
            return self.module_name
        return self.module_name.rsplit('.', maxsplit=1)[-1]

    def get_admin_category_name(self) -> Optional[str]:
        return self.admin_category_name or title_case(self.name)

    @property
    def admins_module(self):
        module_name = self._get_full_module_name(self.admins_module_name)
        if module_name:
            return safe_import_module(module_name)

    def get_admins(self) -> List[AdminTuple]:
        if not self.admins_module:
            return []
        return [AdminTuple(name, admin) for name, admin in
                get_members(self.admins_module, self.type_checker.is_admin)]

    @property
    def bundle_config_module(self):
        module_name = self._get_full_module_name(
            self.bundle_config_module_name)
        if module_name:
            return safe_import_module(module_name)

    def get_bundle_config(self, config_class_name):
        if not self.bundle_config_module:
            return None
        return getattr(self.bundle_config_module, config_class_name, None)

    @property
    def views_module(self):
        module_name = self._get_full_module_name(self.views_module_name)
        if module_name:
            return safe_import_module(module_name)

    def get_blueprint_names(self) -> List[str]:
        if self.blueprint_names != sentinel:
            return self.blueprint_names
        return [self.name]

    def get_blueprints(self) -> List[BlueprintTuple]:
        if not self.views_module:
            return []
        blueprints = dict(get_members(self.views_module,
                                      self.type_checker.is_blueprint))

        blueprint_tuples = []
        for name in self.get_blueprint_names():
            try:
                blueprint = blueprints[name]
            except KeyError as e:
                warn(f'WARNING: Found a views module for the {self.name} '
                     f'bundle, but there was no blueprint named {e.args[0]} '
                     f'in it. Either create one, or customize the '
                     f'blueprint_names kwarg to the Bundle constructor.')
                continue
            blueprint_tuples.append(BlueprintTuple(name, blueprint))
        return blueprint_tuples

    @property
    def commands_module(self) -> Optional[str]:
        module_name = self._get_full_module_name(self.commands_module_name)
        if module_name:
            return safe_import_module(module_name)

    def get_commands(self) -> List[CommandTuple]:
        if not self.commands_module:
            return []

        group_commands = {}
        for _, group in self.get_command_groups():
            group_commands.update(group.commands)

        def is_click_command(name, obj):
            return self.type_checker.is_click_command(name, obj) \
                   and obj.name not in group_commands

        return [CommandTuple(command.name, command) for _, command in
                get_members(self.commands_module, is_click_command)]

    def get_command_group_names(self) -> List[str]:
        if self.command_group_names != sentinel:
            return self.command_group_names
        return [self.name]

    def get_command_groups(self) -> List[CommandGroupTuple]:
        if not self.commands_module:
            return []
        command_groups = dict(get_members(self.commands_module,
                                          self.type_checker.is_click_group))

        command_group_tuples = []
        for name in self.get_command_group_names():
            try:
                command_group = command_groups[name]
            except KeyError as e:
                warn(f'WARNING: Found a commands module for the {self.name} '
                     f'bundle, but there was no command group named {e.args[0]} '
                     f'in it. Either create one, or customize the '
                     f'command_group_names kwarg to the Bundle constructor.')
                continue
            command_group_tuples.append(
                CommandGroupTuple(name, command_group))
        return command_group_tuples

    @property
    def extensions_module(self):
        module_name = self._get_full_module_name(self.extensions_module_name)
        if module_name:
            return safe_import_module(module_name)

    def get_extensions(self) -> List[ExtensionTuple]:
        if not self.extensions_module:
            return []
        extensions = getattr(self.extensions_module, EXTENSIONS, {})
        return self._get_extension_tuples(extensions)

    def get_deferred_extensions(self) -> List[ExtensionTuple]:
        if not self.extensions_module:
            return []
        extensions = getattr(self.extensions_module, DEFERRED_EXTENSIONS, {})
        return self._get_extension_tuples(extensions)

    def _get_extension_tuples(self, extensions: dict):
        extension_tuples = []
        for name, extension in extensions.items():
            if isinstance(extension, (list, tuple)):
                extension, dependencies = extension
            else:
                dependencies = []
            extension_tuples.append(
                ExtensionTuple(name, extension, dependencies))
        return extension_tuples

    @property
    def models_module(self):
        module_name = self._get_full_module_name(self.models_module_name)
        if module_name:
            return safe_import_module(module_name)

    def get_models(self) -> List[ModelTuple]:
        if not self.models_module:
            return []
        return [ModelTuple(name, model) for name, model in
                get_members(self.models_module, self.type_checker.is_model_cls)]

    @property
    def serializers_module(self):
        module_name = self._get_full_module_name(self.serializers_module_name)
        if module_name:
            return safe_import_module(module_name)

    def get_serializers(self) -> List[SerializerTuple]:
        if not self.serializers_module:
            return []
        return [SerializerTuple(name, serializer) for name, serializer in
                get_members(self.serializers_module,
                            self.type_checker.is_serializer_cls)]

    def _get_full_module_name(self, module_name) -> Optional[str]:
        if not module_name:
            return None
        normalized = module_name.replace(self.module_name, '').strip('.')
        return f'{self.module_name}.{normalized}'
