from py_meta_utils import OptionalClass

from .utils import get_boolean_env


class _BundleConfigMetaclass(type):
    current_app = OptionalClass()

    def _set_current_app(cls, app):
        cls.current_app = app


class BundleConfig(metaclass=_BundleConfigMetaclass):
    """
    Base class for bundle configs. Allows access to the app-under-construction
    as it's currently configured from the order bundles were declared in
    ``unchained_config.BUNDLES``. Example usage::

        # your_bundle_root/config.py

        import os

        from flask_unchained import BundleConfig

        class Config(BundleConfig):
            SHOULD_PRETTY_PRINT_JSON = BundleConfig.current_app.config.DEBUG
    """


class _ConfigDefaults:
    DEBUG = get_boolean_env('FLASK_DEBUG', False)


class _DevConfigDefaults:
    DEBUG = get_boolean_env('FLASK_DEBUG', True)


class _TestConfigDefaults:
    TESTING = True
    """
    Tell Flask we're in testing mode.
    """

    WTF_CSRF_ENABLED = False
    """
    Disable CSRF tokens in tests.
    """


__all__ = [
    'BundleConfig',
]
