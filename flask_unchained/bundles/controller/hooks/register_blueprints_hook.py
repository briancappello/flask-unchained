from flask import Blueprint
from flask_unchained import AppFactoryHook, Bundle, FlaskUnchained
from flask_unchained.hooks.views_hook import ViewsHook
from typing import *


class RegisterBlueprintsHook(AppFactoryHook):
    """
    Registers legacy Flask blueprints with the app.
    """

    name = 'blueprints'
    """
    The name of this hook.
    """

    bundle_module_names = ViewsHook.bundle_module_names
    """
    The default module this hook loads from.

    Override by setting the ``blueprints_module_names`` attribute on your
    bundle class.
    """

    bundle_override_module_names_attr = 'blueprints_module_names'
    limit_discovery_to_local_declarations = False
    run_after = ['bundle_blueprints']

    # skipcq: PYL-W0221 (parameters mismatch in overridden method)
    def process_objects(self, app: FlaskUnchained, blueprints: List[Blueprint]):
        """
        Registers discovered blueprints with the app.
        """
        for blueprint in reversed(blueprints):
            # rstrip '/' off url_prefix because views should be declaring their
            # routes beginning with '/', and if url_prefix ends with '/', routes
            # will end up looking like '/prefix//endpoint', which is no good
            url_prefix = (blueprint.url_prefix or '').rstrip('/')
            app.register_blueprint(blueprint, url_prefix=url_prefix)

    def collect_from_bundles(self, bundles: List[Bundle]) -> List[Blueprint]:
        """
        Find blueprints in bundles.
        """
        objects = []
        for bundle in bundles:
            objects += self.collect_from_bundle(bundle)
        return objects

    def collect_from_bundle(self, bundle: Bundle) -> Iterable[Blueprint]:
        """
        Finds blueprints in a bundle hierarchy.
        """
        bundle_blueprints = super().collect_from_bundle(bundle)
        if not bundle_blueprints:
            return []

        blueprint_names = []
        for b in bundle._iter_class_hierarchy():
            for bp_name in getattr(b, 'blueprint_names', [b.name]):
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
        """
        Returns True if ``obj`` is an instance of :class:`flask.Blueprint`.
        """
        return isinstance(obj, Blueprint)
