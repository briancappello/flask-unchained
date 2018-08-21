from .attr_constants import FN_ROUTES_ATTR, NO_ROUTES_ATTR
from .route import Route


def route(rule=None, blueprint=None, defaults=None, endpoint=None,
          is_member=False, methods=None, only_if=None, **rule_options):
    """
    Decorator to set default route rules for a view function. The arguments this
    function accepts are very similar to Flask's ``app.route`` and ``bp.route``,
    however, the ``is_member`` perhaps deserves an example::

        class UserResource(ModelResource):
            model = User
            member_param = '<int:id>'
            include_methods = ['list', 'get']

            @route(is_member=True, methods=['POST'])
            def set_profile_pic(user):
                # do stuff

        routes = lambda: [
            resource(UserResource)
        ]

        # UserResource.list             => GET  /users
        # UserResource.get              => GET  /users/<int:id>
        # UserResource.set_profile_pic  => POST /users/<int:id>/set-profile-pic

    :param rule: The URL rule.
    :param defaults: Any default values for parameters in the URL rule.
    :param endpoint: The endpoint name of this view. Determined automatically if left
                     unspecified.
    :param is_member: Whether or not this view is for a
                      :class:`~flask_unchained.bundles.resource.resource.Resource`
                      member method.
    :param methods: A list of HTTP methods supported by this view. Defaults to
                    ``['GET']``.
    :param only_if: A boolean or callable to dynamically determine whether or not to
                    register this route with the app.
    :param rule_options: Other kwargs passed on to :class:`~werkzeug.routing.Rule`.
    """
    def wrapper(fn):
        fn_routes = getattr(fn, FN_ROUTES_ATTR, [])
        route = Route(rule, fn, blueprint=blueprint, defaults=defaults,
                      endpoint=endpoint, is_member=is_member, methods=methods,
                      only_if=only_if, **rule_options)
        setattr(fn, FN_ROUTES_ATTR, fn_routes + [route])
        return fn

    if callable(rule):
        fn = rule
        rule = None
        return wrapper(fn)
    return wrapper


def no_route(arg=None):
    """
    Decorator to mark a
    :class:`~flask_unchained.bundles.controller.controller.Controller` or
    :class:`~flask_unchained.bundles.resource.resource.Resource` method as not a route.
    """
    def wrapper(fn):
        setattr(fn, NO_ROUTES_ATTR, True)
        return fn

    if callable(arg):
        return wrapper(arg)
    return wrapper
