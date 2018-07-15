import inspect

from flask_unchained.string_utils import snake_case

from .constants import _missing
from .utils import join, method_name_to_url


class Route:
    """
    This is a semi-private class that you most likely shouldn't use directly.
    Instead, you should use the public functions in `routes`, and the `route`
    and `no_route` decorators.

    This class is used to store an **intermediate** representation of route
    details as an attribute on view functions and class view methods.

    Most notably, this class's rule and full_rule attributes may not represent
    the final url rule that gets registered with Flask (especially true for
    Controller and Resource view methods - use TheControllerClass.route_rule).

    Further gotchas with Controller and Resource routes include that their
    view_func must be finalized from the outside using
    TheControllerClass.method_as_view, and for subresources, the blueprint
    specified here can (will) be overridden by the parent resource's blueprint.
    (If it does get overridden, a warning will at least be issued.)
    """
    def __init__(self, rule, view_func, blueprint=None, defaults=None,
                 endpoint=None, is_member=False, methods=None, only_if=None,
                 **rule_options):
        self._blueprint = blueprint
        self._defaults = defaults or {}
        self._endpoint = endpoint
        self._is_member = is_member
        self._methods = methods
        self._only_if = only_if
        self._rule = rule
        self.rule_options = rule_options
        self.view_func = view_func

        # extra private (should only be used by controller metaclasses)
        self._controller_name = None

    def should_register(self, app):
        if self.only_if is None:
            return True
        elif callable(self.only_if):
            return self.only_if(app)
        return bool(self.only_if)

    @property
    def blueprint(self):
        if self._blueprint is _missing:
            return None
        return self._blueprint

    @blueprint.setter
    def blueprint(self, blueprint):
        self._blueprint = blueprint

    @property
    def bp_prefix(self):
        if not self.blueprint:
            return None
        return self.blueprint.url_prefix

    @property
    def bp_name(self):
        if not self.blueprint:
            return None
        return self.blueprint.name

    @property
    def defaults(self):
        if self._defaults is _missing:
            return {}
        return self._defaults

    @defaults.setter
    def defaults(self, defaults):
        self._defaults = defaults or {}

    @property
    def endpoint(self):
        if self._endpoint:
            return self._endpoint
        elif self._controller_name:
            suffix = f'{snake_case(self._controller_name)}.{self.method_name}'
            return self.bp_name and f'{self.bp_name}.{suffix}' or suffix
        elif self.bp_name:
            return f'{self.bp_name}.{self.method_name}'
        return f'{self.view_func.__module__}.{self.method_name}'

    @endpoint.setter
    def endpoint(self, endpoint):
        self._endpoint = endpoint

    @property
    def is_member(self):
        if self._is_member is _missing:
            return False
        return self._is_member

    @is_member.setter
    def is_member(self, is_member):
        self._is_member = is_member

    @property
    def method_name(self):
        if isinstance(self.view_func, str):
            return self.view_func
        return self.view_func.__name__

    @property
    def methods(self):
        return getattr(self.view_func, 'methods', self._methods) or ['GET']

    @methods.setter
    def methods(self, methods):
        self._methods = methods

    @property
    def module_name(self):
        if not self.view_func:
            return None
        return inspect.getmodule(self.view_func).__name__

    @property
    def only_if(self):
        if self._only_if is _missing:
            return None
        return self._only_if

    @only_if.setter
    def only_if(self, only_if):
        self._only_if = only_if

    @property
    def rule(self):
        if self._rule:
            return self._rule
        elif self._controller_name:
            return None
        return method_name_to_url(self.method_name)

    @rule.setter
    def rule(self, rule):
        self._rule = rule

    @property
    def full_rule(self):
        if not self.rule:
            raise Exception(f'{self} not fully initialized (missing url rule)')
        return join(self.bp_prefix, self.rule)

    def copy(self):
        new = object.__new__(Route)
        new.__dict__ = self.__dict__.copy()
        return new

    @property
    def full_name(self):
        if not self.view_func:
            return None

        prefix = self.view_func.__module__
        if self._controller_name:
            prefix = f'{prefix}.{self._controller_name}'
        return f'{prefix}.{self.method_name}'

    def __repr__(self):
        return f'<Route endpoint={self.endpoint}>'
