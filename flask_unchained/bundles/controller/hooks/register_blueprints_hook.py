from flask import Blueprint, Flask
from flask_unchained import AppFactoryHook, Bundle
from typing import *


class RegisterBlueprintsHook(AppFactoryHook):
    bundle_module_name = 'views'
    bundle_override_module_name_attr = 'views_module_name'
    name = 'blueprints'
    run_after = ['bundle_template_folders']

    action_category = 'blueprints'
    action_table_columns = ['name', 'url_prefix']
    action_table_converter = lambda bp: [bp.name, bp.url_prefix]

    _limit_discovery_to_local_declarations = False

    def run_hook(self, app: Flask, bundles: List[Type[Bundle]]):
        super().run_hook(app, bundles)

    def process_objects(self, app: Flask, blueprints: List[Blueprint]):
        for blueprint in reversed(blueprints):
            # rstrip '/' off url_prefix because views should be declaring their
            # routes beginning with '/', and if url_prefix ends with '/', routes
            # will end up looking like '/prefix//endpoint', which is no good
            url_prefix = (blueprint.url_prefix or '').rstrip('/')
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            self.log_action(blueprint)

    def collect_from_bundles(self, bundles: List[Type[Bundle]],
                             ) -> List[Blueprint]:
        objects = []
        for bundle in bundles:
            objects += self.collect_from_bundle(bundle)
        return objects

    def collect_from_bundle(self, bundle: Type[Bundle]) -> Iterable[Blueprint]:
        bundle_blueprints = super().collect_from_bundle(bundle)
        if not bundle_blueprints:
            return []

        blueprint_names = []
        for bundle in bundle.iter_class_hierarchy():
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
