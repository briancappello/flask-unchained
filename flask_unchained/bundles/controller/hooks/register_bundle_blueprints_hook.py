from flask import Flask, Blueprint
from flask.blueprints import BlueprintSetupState as BaseSetupState
from flask.helpers import _endpoint_from_view_func
from flask_unchained import AppFactoryHook, Bundle
from typing import List

# FIXME test template resolution order when this is used in combination with
# RegisterBlueprintsHook


class BlueprintSetupState(BaseSetupState):
    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        """A helper method to register a rule (and optionally a view function)
        to the application.  The endpoint is automatically prefixed with the
        blueprint's name.
        """
        if self.url_prefix:
            rule = self.url_prefix + rule
        options.setdefault('subdomain', self.subdomain)
        if endpoint is None:
            endpoint = _endpoint_from_view_func(view_func)
        defaults = self.url_defaults
        if 'defaults' in options:
            defaults = dict(defaults, **options.pop('defaults'))
        self.app.add_url_rule(rule, endpoint, view_func, defaults=defaults, **options)


class BundleBlueprint(Blueprint):
    """
    The purpose of this class is to register a custom template folder and/or
    static folder with Flask. And it seems the only way to do that is to
    pretend to be a blueprint...
    """
    url_prefix = None

    def __init__(self, bundle: Bundle):
        self.bundle = bundle
        super().__init__(bundle.name, bundle.module_name,
                         static_folder=bundle.static_folder,
                         static_url_path=bundle.static_url_path,
                         template_folder=bundle.template_folder)

    def make_setup_state(self, app, options, first_registration=False):
        return BlueprintSetupState(self, app, options, first_registration)

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        """Like :meth:`Flask.add_url_rule` but for a blueprint.  The endpoint for
        the :func:`url_for` function is prefixed with the name of the blueprint.

        Overridden to allow dots in endpoint names
        """
        self.record(lambda s: s.add_url_rule(rule, endpoint, view_func,
                                             register_with_babel=False, **options))

    def register(self, app, options, first_registration=False):
        """Called by :meth:`Flask.register_blueprint` to register a blueprint
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
                               endpoint=f'{self.bundle.name}.static')

        for deferred in self.bundle._deferred_functions:
            deferred(self)

        for deferred in self.deferred_functions:
            deferred(state)

    def __repr__(self):
        return f'<BundleBlueprint "{self.name}">'


class RegisterBundleBlueprintsHook(AppFactoryHook):
    bundle_module_name = None
    name = 'bundle_template_folders'
    run_before = ['blueprints']

    action_category = 'template_folders'
    action_table_columns = ['name', 'folder']
    action_table_converter = lambda bp: [bp.name, bp.template_folder]

    def run_hook(self, app: Flask, bundles: List[Bundle]):
        for bundle_ in reversed(bundles):
            for bundle in bundle_.iter_class_hierarchy(reverse=False):
                if (bundle.template_folder
                        or bundle.static_folder
                        or bundle.has_views()):
                    bp = BundleBlueprint(bundle)
                    for route in self.store.bundle_routes.get(bundle.name, []):
                        bp.add_url_rule(route.full_rule,
                                        defaults=route.defaults,
                                        endpoint=route.endpoint,
                                        methods=route.methods,
                                        view_func=route.view_func,
                                        **route.rule_options)
                    app.register_blueprint(bp)
                    self.log_action(bp)
