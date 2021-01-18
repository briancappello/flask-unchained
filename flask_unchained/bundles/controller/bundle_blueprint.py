from flask import Blueprint as BaseBlueprint
from flask import send_from_directory as _send_from_directory
from flask.blueprints import BlueprintSetupState as BaseBlueprintSetupState

from flask_unchained import Bundle
from werkzeug.exceptions import NotFound


class BundleBlueprintSetupState(BaseBlueprintSetupState):
    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        """
        A helper method to register a rule (and optionally a view function)
        to the application.

        Overridden to not prefix endpoints with the blueprint name (bundle name).
        """
        if self.url_prefix:
            rule = self.url_prefix + rule
        options.setdefault('subdomain', self.subdomain)
        if endpoint is None:
            endpoint = view_func.__name__
        defaults = self.url_defaults
        if 'defaults' in options:
            defaults = dict(defaults, **options.pop('defaults'))
        self.app.add_url_rule(rule, endpoint, view_func, defaults=defaults, **options)


class BundleBlueprint(BaseBlueprint):
    """
    This is a semi-private class to make blueprints compatible with bundles and
    their hierarchies. Bundle blueprints are created automatically for each bundle
    that has a template folder and/or static folder. If *any* bundle in the hierarchy
    has views/routes that should be registered with the app, then those views/routes
    will get registered *only* with the :class:`BundleBlueprint` for the *top-most*
    bundle in the hierarchy.
    """
    url_prefix = None

    def __init__(self, bundle: Bundle):
        self.bundle = bundle
        super().__init__(bundle._blueprint_name, bundle.module_name,
                         static_url_path=bundle.static_url_path,
                         template_folder=None if bundle.is_single_module else bundle.template_folder)

    @property
    def has_static_folder(self):
        return bool(self.bundle._static_folders)

    def send_static_file(self, filename):
        if not self.has_static_folder:
            raise RuntimeError(f'No static folder found for {self.bundle.name}')
        # Ensure get_send_file_max_age is called in all cases.
        # Here, we ensure get_send_file_max_age is called for Blueprints.
        cache_timeout = self.get_send_file_max_age(filename)
        for directory in self.bundle._static_folders:
            try:
                return _send_from_directory(directory, filename,
                                            cache_timeout=cache_timeout)
            except NotFound:
                continue
        raise NotFound()

    def make_setup_state(self, app, options, first_registration=False):
        return BundleBlueprintSetupState(self, app, options, first_registration)

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        """
        Like :meth:`~flask.Flask.add_url_rule` but for a blueprint.
        """
        self.record(lambda s: s.add_url_rule(rule, endpoint, view_func,
                                             register_with_babel=False, **options))

    def register(self, app, options, first_registration=False):
        """
        Called by :meth:`~flask.Flask.register_blueprint` to register a blueprint
        on the application.  This can be overridden to customize the register
        behavior.  Keyword arguments from
        :func:`~flask.Flask.register_blueprint` are directly forwarded to this
        method in the `options` dictionary.
        """
        self._got_registered_once = True
        state = self.make_setup_state(app, options, first_registration)
        if self.has_static_folder:
            state.add_url_rule(self.static_url_path + '/<path:filename>',
                               view_func=self.send_static_file,
                               endpoint=f'{self.bundle._blueprint_name}.static',
                               register_with_babel=False)

        for deferred in self.bundle._deferred_functions:
            deferred(self)

        for deferred in self.deferred_functions:
            deferred(state)

    def __repr__(self):
        return f'BundleBlueprint(name={self.name!r}, bundle={self.bundle!r})'


__all__ = [
    'BundleBlueprint',
]
