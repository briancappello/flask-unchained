from flask_unchained import AppFactoryHook, FlaskUnchained
from typing import *

from ..object_types import MutationsObjectType


class RegisterGrapheneMutationsHook(AppFactoryHook):
    """
    Registers Graphene Mutations with the Graphene Bundle.
    """

    name = 'graphene_mutations'
    """
    The name of this hook.
    """

    bundle_module_names = ['graphene.mutations', 'graphene.schema']
    """
    The default module this hook loads from.

    Override by setting the ``graphene_mutations_module_names`` attribute on your
    bundle class.
    """

    bundle_override_module_names_attr = 'graphene_mutations_module_names'
    run_after = ['graphene_types']

    # skipcq: PYL-W0221 (parameters mismatch in overridden method)
    def process_objects(self,
                        app: FlaskUnchained,
                        mutations: Dict[str, MutationsObjectType]):
        """
        Register discovered mutations with the Graphene Bundle.
        """
        self.bundle.mutations = mutations

    def type_check(self, obj: Any):
        """
        Returns True if ``obj`` is a subclass of
        :class:`~flask_unchained.bundles.graphene.MutationsObjectType`.
        """
        is_subclass = isinstance(obj, type) and issubclass(obj, MutationsObjectType)
        return is_subclass and obj != MutationsObjectType and (
                not hasattr(obj, 'Meta') or not getattr(obj.Meta, 'abstract', False))
