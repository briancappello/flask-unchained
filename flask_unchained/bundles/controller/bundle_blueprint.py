from flask import Blueprint as BaseBlueprint
from flask import send_from_directory as _send_from_directory
from flask.blueprints import BlueprintSetupState as BaseBlueprintSetupState
from flask.blueprints import _endpoint_from_view_func

from flask_unchained import Bundle
from werkzeug.exceptions import NotFound


class BundleBlueprintSetupState(BaseBlueprintSetupState):
    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        """
        A helper method to register a rule (and optionally a view function)
        to the application.

        Overridden to conditionally prefix endpoints with the bundle name.
        """
        if self.url_prefix is not None:
            if rule:
                rule = "/".join((self.url_prefix.rstrip("/"), rule.lstrip("/")))
            else:
                rule = self.url_prefix
        options.setdefault('subdomain', self.subdomain)
        if endpoint is None:
            endpoint = _endpoint_from_view_func(view_func)
        # only automatically prefix endpoints if no prefix was explicitly provided
        if '.' not in endpoint:
            name_prefix = getattr(self, "name_prefix", "")
            endpoint = f'{name_prefix}{self.blueprint.name}.{endpoint}'
        defaults = self.url_defaults
        if 'defaults' in options:
            defaults = dict(defaults, **options.pop('defaults'))
        self.app.add_url_rule(rule, endpoint, view_func, defaults=defaults, **options)

    def register_deferred_bundle_functions(self):
        bp = self.blueprint
        for deferred in bp.bundle._deferred_functions:
            deferred(bp)


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
        super().__init__(
            name=bundle._blueprint_name,
            import_name=bundle.module_name,
            static_url_path=bundle.static_url_path,
            template_folder=None if bundle.is_single_module else bundle.template_folder,
            root_path=bundle.root_path,
        )
        self.bundle = bundle
        self.deferred_functions = [
            BundleBlueprintSetupState.register_deferred_bundle_functions,
        ]

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

    def __repr__(self):
        return f'BundleBlueprint(name={self.name!r}, bundle={self.bundle!r})'


__all__ = [
    'BundleBlueprint',
]
