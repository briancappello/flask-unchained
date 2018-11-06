from flask_unchained import AppFactoryHook, Bundle, FlaskUnchained
from flask_unchained.bundle_blueprint import BundleBlueprint
from typing import *

# FIXME test template resolution order when this is used in combination with
# RegisterBlueprintsHook


class RegisterBundleBlueprintsHook(AppFactoryHook):
    """
    Registers a blueprint for each bundle with views and/or template/static folders.
    """

    bundle_module_name = None
    name = 'bundle_blueprints'
    run_before = ['blueprints']

    def run_hook(self, app: FlaskUnchained, bundles: List[Bundle]):
        for bundle_ in reversed(bundles):
            for bundle in bundle_._iter_class_hierarchy(reverse=False):
                if (bundle.template_folder
                        or bundle._static_folders
                        or bundle._has_views()):
                    bp = BundleBlueprint(bundle)
                    for route in self.bundle.bundle_routes.get(bundle.module_name, []):
                        bp.add_url_rule(route.full_rule,
                                        defaults=route.defaults,
                                        endpoint=route.endpoint,
                                        methods=route.methods,
                                        view_func=route.view_func,
                                        **route.rule_options)
                    app.register_blueprint(bp)
