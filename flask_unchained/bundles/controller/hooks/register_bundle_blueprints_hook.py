from flask_unchained import AppFactoryHook, Bundle, FlaskUnchained
from typing import *

from ..bundle_blueprint import BundleBlueprint

# FIXME test template resolution order when this is used in combination with
# RegisterBlueprintsHook


class RegisterBundleBlueprintsHook(AppFactoryHook):
    """
    Registers a bundle blueprint for each bundle with views and/or template/static folders.
    """

    name = 'bundle_blueprints'
    """
    The name of this hook.
    """

    bundle_module_names = None
    run_before = ['blueprints']

    def run_hook(self,
                 app: FlaskUnchained,
                 bundles: List[Bundle],
                 unchained_config: Optional[Dict[str, Any]] = None,
                 ) -> None:
        """
        Register blueprints for bundles, where necessary.
        """
        for bundle_ in reversed(bundles):
            for bundle in bundle_._iter_class_hierarchy(mro=True):
                if (bundle.template_folder
                        or bundle._static_folders
                        or bundle._has_views):
                    bp = BundleBlueprint(bundle)
                    for route in self.bundle.bundle_routes.get(bundle.module_name, []):
                        bp.add_url_rule(route.full_rule,
                                        defaults=route.defaults,
                                        endpoint=route.endpoint,
                                        methods=route.methods,
                                        view_func=route.view_func,
                                        **route.rule_options)
                    app.register_blueprint(bp)
