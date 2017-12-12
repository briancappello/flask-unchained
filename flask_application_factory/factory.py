from flask import Flask
from typing import List
from warnings import warn

from .bundle import Bundle
from .extensions import resolve_extension_order
from .tuples import ExtensionTuple
from .type_checker import TypeChecker
from .utils import get_members, safe_import_module


class FlaskApplicationFactory:
    def __init__(self):
        self.type_checker = TypeChecker()
        self.bundles = []
        self.extensions = {}
        self.models = {}
        self.serializers = {}

    def create_app(self, import_name, config_class, **kwargs):
        """Creates a Flask application.

        :param str import_name: The import name of the app.
        :param object config_class: The config class to use.
        :param dict kwargs: Extra kwargs to pass to the Flask constructor.
        """
        # WARNING: HERE BE DRAGONS!!! (the order of these calls is very important)
        self.bundles = self._load_bundles(config_class)

        for k, v in getattr(config_class, 'FLASK_KWARGS', {}).items():
            if k not in kwargs:
                kwargs[k] = v

        app = Flask(import_name, **kwargs)

        self._pre_configure_app(app, config_class)
        self.configure_app(app, config_class)

        self._pre_register_extensions(app)
        self.register_extensions(app, self.get_extensions())
        self._post_register_extensions(app)

        self.register_blueprints(app)
        self.register_models(app)
        self.register_serializers(app)

        # deferred extensions
        self._pre_register_deferred_extensions(app)
        self.register_extensions(app, self.get_deferred_extensions())
        self._post_register_deferred_extensions(app)

        self.register_admins(app)
        self.register_cli_commands(app)
        self.register_shell_context(app)

        self.finalize_app(app)

        return app

    def _pre_configure_app(self, app: Flask, config_class):
        for bundle in self.bundles:
            bundle.pre_configure_app(app, config_class, self.bundles)

    def configure_app(self, app: Flask, config_class):
        app.config.from_object(config_class)

    def _pre_register_extensions(self, app: Flask):
        for bundle in self.bundles:
            bundle.post_configure_app(app, self.bundles)

    def get_extensions(self) -> List[ExtensionTuple]:
        extension_tuples = []
        for bundle in self.bundles:
            extension_tuples += bundle.get_extensions()
        return extension_tuples

    def get_deferred_extensions(self) -> List[ExtensionTuple]:
        deferred_extension_tuples = []
        for bundle in self.bundles:
            deferred_extension_tuples += bundle.get_deferred_extensions()
        return deferred_extension_tuples

    def register_extensions(self, app: Flask, extension_tuples: List[ExtensionTuple]):
        order = resolve_extension_order(extension_tuples)
        extensions = {extension.name: extension.extension
                      for extension in extension_tuples}
        for name in order:
            extensions[name].init_app(app)
        self.extensions.update(extensions)

    def _post_register_extensions(self, app):
        for bundle in self.bundles:
            bundle.post_register_extensions(app, self.bundles)

    def _pre_register_deferred_extensions(self, app):
        for bundle in self.bundles:
            bundle.pre_register_deferred_extensions(app, self.bundles)

    def _post_register_deferred_extensions(self, app):
        for bundle in self.bundles:
            bundle.post_register_deferred_extensions(app, self.bundles)

    def register_blueprints(self, app: Flask):
        """Register bundle views."""
        # disable strict_slashes on all routes by default
        if not app.config.get('STRICT_SLASHES', False):
            app.url_map.strict_slashes = False

        for bundle in self.bundles:
            for name, blueprint in bundle.get_blueprints():
                # rstrip '/' off url_prefix because views should be declaring their
                # routes beginning with '/', and if url_prefix ends with '/', routes
                # will end up looking like '/prefix//endpoint', which is no good
                url_prefix = (blueprint.url_prefix or '').rstrip('/')
                app.register_blueprint(blueprint, url_prefix=url_prefix)

    def register_models(self, app: Flask):
        """Register bundle models."""
        for bundle in self.bundles:
            for name, model_class in bundle.get_models():
                self.models[name] = model_class
        setattr(app, 'models', self.models)

    def register_serializers(self, app: Flask):
        """Register bundle serializers."""
        for bundle in self.bundles:
            for name, serializer_class in bundle.get_serializers():
                self.serializers[name] = serializer_class
        setattr(app, 'serializers', self.serializers)

    def register_admins(self, app: Flask):
        """Register bundle admins."""
        admin = self.extensions.get('admin')
        db = self.extensions.get('db')

        for bundle in self.bundles:
            if bundle.admin_icon_class:
                admin.category_icon_classes[bundle.get_admin_category_name()] = bundle.admin_icon_class

            for name, ModelAdmin in bundle.get_admins():
                model_admin = ModelAdmin(ModelAdmin.model,
                                         db.session,
                                         category=bundle.admin_category_name,
                                         name=ModelAdmin.model.__plural_label__)

                # workaround upstream bug where certain values set as
                # class attributes get overridden by the constructor
                model_admin.menu_icon_value = getattr(ModelAdmin, 'menu_icon_value', None)
                if model_admin.menu_icon_value:
                    model_admin.menu_icon_type = getattr(ModelAdmin, 'menu_icon_type', None)

                admin.add_view(model_admin)

    def register_cli_commands(self, app: Flask):
        """Register all the Click commands declared in :file:`backend/commands` and
        each bundle's commands"""
        commands = []
        for bundle in self.bundles:
            commands += list(bundle.get_commands())
            commands += list(bundle.get_command_groups())

        for name, command in commands:
            if name in app.cli.commands:
                warn(f'Command name conflict: "{name}" is taken.')
                continue
            app.cli.add_command(command, name)

    def register_shell_context(self, app: Flask):
        """Register variables to automatically import when running `python manage.py shell`."""
        def shell_context():
            ctx = {}
            ctx.update(self.extensions)
            ctx.update(self.models)
            ctx.update(self.serializers)
            return ctx
        app.shell_context_processor(shell_context)

    def finalize_app(self, app):
        for bundle in self.bundles:
            bundle.finalize_app(app, self.bundles)

    def _load_bundles(self, config_class) -> List[Bundle]:
        bundles = []
        for bundle_or_module_name in config_class.BUNDLES:
            if self.type_checker.is_bundle_cls(None, bundle_or_module_name):
                bundles.append(bundle_or_module_name())
                continue

            module = safe_import_module(bundle_or_module_name)
            bundle_found = False
            for name, bundle in get_members(module, self.type_checker.is_bundle_cls):
                bundles.append(bundle())
                bundle_found = True

            if not bundle_found:
                warn(f'Unable to find a Bundle class for the '
                     f'{bundle_or_module_name} bundle! Please make sure it\'s '
                     f'installed and that there is a Bundle subclass in the '
                     f'package\'s __init__.py file.')

        for bundle in bundles:
            admin_base_classes = getattr(bundle, 'admin_base_classes', None)
            if admin_base_classes:
                TypeChecker.admin_base_classes += list(admin_base_classes)

            model_base_classes = getattr(bundle, 'model_base_classes', None)
            if model_base_classes:
                TypeChecker.model_base_classes += list(model_base_classes)

            serializer_base_classes = getattr(bundle, 'serializer_base_classes', None)
            if serializer_base_classes:
                TypeChecker.serializer_base_classes += list(serializer_base_classes)

        return bundles
