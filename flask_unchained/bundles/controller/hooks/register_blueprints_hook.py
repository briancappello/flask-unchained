from flask import Blueprint
from flask_unchained import AppFactoryHook, Bundle, FlaskUnchained
from typing import *


class RegisterBlueprintsHook(AppFactoryHook):
    """
    Registers blueprints with the app.
    """

    bundle_module_name = 'views'
    bundle_override_module_name_attr = 'blueprints_module_name'
    name = 'blueprints'
    run_after = ['bundle_blueprints']

    limit_discovery_to_local_declarations = False

    def process_objects(self, app: FlaskUnchained, blueprints: List[Blueprint]):
        for blueprint in reversed(blueprints):
            # rstrip '/' off url_prefix because views should be declaring their
            # routes beginning with '/', and if url_prefix ends with '/', routes
            # will end up looking like '/prefix//endpoint', which is no good
            url_prefix = (blueprint.url_prefix or '').rstrip('/')
            app.register_blueprint(blueprint, url_prefix=url_prefix)

    def collect_from_bundles(self, bundles: List[Bundle]) -> List[Blueprint]:
        objects = []
        for bundle in bundles:
            objects += self.collect_from_bundle(bundle)
        return objects

    def collect_from_bundle(self, bundle: Bundle) -> Iterable[Blueprint]:
        bundle_blueprints = super().collect_from_bundle(bundle)
        if not bundle_blueprints:
            return []

        blueprint_names = []
        for bundle in bundle._iter_class_hierarchy():
            for bp_name in getattr(bundle, 'blueprint_names', [bundle.name]):
                if bp_name not in blueprint_names:
                    blueprint_names += [bp_name]

        blueprints = []
        for name in blueprint_names:
            try:
                blueprint = bundle_blueprints[name]
            except KeyError:
                from warnings import warn
                warn(f'WARNING: Found a views module for the {bundle.name} '
                     f'bundle, but there was no blueprint named {name} '
                     f'in it. Either create one, or customize the bundle\'s '
                     f'`blueprint_names` class attribute.')
                continue
            blueprints.append(blueprint)
        return reversed(blueprints)

    def type_check(self, obj):
        return isinstance(obj, Blueprint)
