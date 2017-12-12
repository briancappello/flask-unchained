import click
import inspect

from flask import Blueprint


class TypeChecker:
    admin_base_classes = []
    model_base_classes = []
    serializer_base_classes = []

    def is_admin(self, name, obj) -> bool:
        return self._issubclass(obj, self.admin_base_classes)

    def is_blueprint(self, name, obj) -> bool:
        return isinstance(obj, Blueprint)

    def is_bundle_cls(self, name, obj) -> bool:
        from .bundle import Bundle
        return inspect.isclass(obj) and issubclass(obj, Bundle) and obj != Bundle

    def is_click_command(self, name, obj):
        return isinstance(obj, click.Command) and not isinstance(obj, click.Group)

    def is_click_group(self, name, obj) -> bool:
        return isinstance(obj, click.Group)

    def is_extension(self, name, obj) -> bool:
        return not inspect.isclass(obj) and hasattr(obj, 'init_app')

    def is_model_cls(self, name, obj) -> bool:
        return self._issubclass(obj, self.model_base_classes)

    def is_serializer_cls(self, name, obj) -> bool:
        return self._issubclass(obj, self.serializer_base_classes)

    def _issubclass(self, obj, bases):
        if not inspect.isclass(obj):
            return False
        bases = tuple(set(bases))
        return issubclass(obj, bases) and obj not in bases
