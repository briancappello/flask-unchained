import inspect

from flask_unchained.string_utils import snake_case
from py_meta_utils import _missing

from .utils import (join, method_name_to_url, rename_parent_resource_param_name,
                    controller_name, get_param_tuples)


class Route:
    """
    This is a semi-private class that you most likely shouldn't use directly.
    Instead, you should use the public functions in :ref:`api/bundles/controller:Routes`,
    and the :func:`~flask_unchained.route` and :func:`~flask_unchained.no_route`
    decorators.

    This class is used to store an *intermediate* representation of route details as
    an attribute on view functions and class view methods. Most notably, this class's
    :attr:`rule` and :attr:`full_rule` attributes may not represent the final url rule
    that gets registered with :class:`~flask.Flask`.

    Further gotchas with :class:`~flask_unchained.Controller` and
    :class:`~flask_unchained.Resource` routes include that their view_func must be
    finalized from the outside using ``TheControllerClass.method_as_view``.
    """
    def __init__(self, rule, view_func, blueprint=None, defaults=None,
                 endpoint=None, is_member=False, methods=None, only_if=None,
                 **rule_options):
        self._blueprint = blueprint
        self._defaults = defaults or {}
        self._endpoint = endpoint
        self._methods = methods
        self._only_if = only_if
        self._rule = rule
        self.rule_options = rule_options
        self.view_func = view_func

        # private
        self._controller_cls = None
        self._member_param = None
        self._unique_member_param = None
        self._parent_resource_cls = None
        self._parent_member_param = None

        self._is_member = is_member
        """
        Whether or not this route should be a member method of the parent resource.
        """

        self._is_member_method = False
        """
        Whether or not this route is a member method of this route's resource class.
        """

    def should_register(self, app):
        """
        Determines whether or not this route should be registered with the app,
        based on :attr:`only_if`.
        """
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
        """
        The URL defaults for this route.
        """
        if self._defaults is _missing:
            return {}
        return self._defaults

    @defaults.setter
    def defaults(self, defaults):
        self._defaults = defaults or {}

    @property
    def endpoint(self):
        """
        The endpoint for this route.
        """
        if self._endpoint:
            return self._endpoint
        elif self._controller_cls:
            endpoint = f'{snake_case(self._controller_cls.__name__)}.{self.method_name}'
            return endpoint if not self.bp_name else f'{self.bp_name}.{endpoint}'
        elif self.bp_name:
            return f'{self.bp_name}.{self.method_name}'
        return f'{self.view_func.__module__}.{self.method_name}'

    @endpoint.setter
    def endpoint(self, endpoint):
        self._endpoint = endpoint

    @property
    def is_member(self):
        """
        Whether or not this route is for a resource member route.
        """
        if self._is_member is _missing:
            return False
        return self._is_member

    @is_member.setter
    def is_member(self, is_member):
        self._is_member = is_member

    @property
    def method_name(self):
        """
        The string name of this route's view function.
        """
        if isinstance(self.view_func, str):
            return self.view_func
        return self.view_func.__name__

    @property
    def methods(self):
        """
        The HTTP methods supported by this route.
        """
        return getattr(self.view_func, 'methods', self._methods) or ['GET']

    @methods.setter
    def methods(self, methods):
        self._methods = methods

    @property
    def module_name(self):
        """
        The module where this route's view function was defined.
        """
        if not self.view_func:
            return None
        elif self._controller_cls:
            rv = inspect.getmodule(self._controller_cls).__name__
            return rv
        return inspect.getmodule(self.view_func).__name__

    @property
    def only_if(self):
        """
        A boolean or callable to determine whether or not this route should be
        registered with the app. Defaults to ``True``.
        """
        if self._only_if is _missing:
            return True
        return self._only_if

    @only_if.setter
    def only_if(self, only_if):
        self._only_if = only_if

    @property
    def rule(self):
        """
        The (partial) url rule for this route.
        """
        if self._rule:
            return self._rule
        return self._make_rule(member_param=self._member_param,
                               unique_member_param=self._unique_member_param)

    @rule.setter
    def rule(self, rule):
        if rule is not None and not rule.startswith('/'):
            rule = '/' + rule
        self._rule = rule

    @property
    def full_rule(self):
        """
        The full url rule for this route, including any blueprint prefix.
        """
        return join(self.bp_prefix, self.rule, trailing_slash=self.rule.endswith('/'))

    def _make_rule(self, url_prefix=None, member_param=None, unique_member_param=None):
        if member_param is not None:
            self._member_param = member_param
        if unique_member_param is not None:
            self._unique_member_param = unique_member_param

        if self._rule:
            return join(url_prefix, self._rule, trailing_slash=self._rule.endswith('/'))
        elif self._controller_cls:
            rule = method_name_to_url(self.method_name)
            if (self._is_member or self._is_member_method) and not member_param:
                raise Exception('member_param argument is required')
            if self._is_member_method:
                rule = member_param
            elif self._is_member:
                rule = rename_parent_resource_param_name(self, join(member_param, rule))
            return join(url_prefix, rule)
        return method_name_to_url(self.method_name)

    @property
    def unique_member_param(self):
        if self._unique_member_param:
            return self._unique_member_param

        ctrl_name = controller_name(self._controller_cls)
        type_, name = get_param_tuples(self._member_param)[0]
        return f'<{type_}:{ctrl_name}_{name}>'

    def copy(self):
        new = object.__new__(Route)
        new.__dict__ = self.__dict__.copy()
        return new

    @property
    def full_name(self):
        """
        The full name of this route's view function, including the module path
        and controller name, if any.
        """
        if not self.view_func:
            return None

        prefix = self.view_func.__module__
        if self._controller_cls:
            prefix = f'{prefix}.{self._controller_cls.__name__}'
        return f'{prefix}.{self.method_name}'

    def __repr__(self):
        try:
            return f'Route(endpoint={self.endpoint}, rule={self.rule})'
        except:
            return f'Route(endpoint={self.endpoint})'
