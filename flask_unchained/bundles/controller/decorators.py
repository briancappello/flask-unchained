from enum import Enum
from functools import wraps
from http import HTTPStatus

from flask import abort, request
from flask_unchained.string_utils import snake_case
from py_meta_utils import _missing

try:
    from sqlalchemy_unchained import BaseModel as Model
except ImportError:
    Model = None

from .attr_constants import FN_ROUTES_ATTR, NO_ROUTES_ATTR
from .route import Route


def route(rule=None, blueprint=None, defaults=None, endpoint=None,
          is_member=False, methods=None, only_if=_missing, **rule_options):
    """
    Decorator to set default route rules for a view function. The arguments this
    function accepts are very similar to Flask's :meth:`~flask.Flask.route`,
    however, the ``is_member`` perhaps deserves an example::

        class UserResource(ModelResource):
            class Meta:
                model = User
                member_param = '<int:id>'
                include_methods = ['list', 'get']

            @route(is_member=True, methods=['POST'])
            def set_profile_pic(user):
                # do stuff

        # registered like so in your ``app_bundle/routes.py``:
        routes = lambda: [
            resource(UserResource),
        ]

        # results in the following routes:
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
    :class:`~flask_unchained.bundles.controller.resource.Resource` method as *not*
    a route. For example::

        class SiteController(Controller):
            @route('/')
            def index():
                return self.render('index')

            def about():
                return self.render('about', stuff=self.utility_method())

            @no_route
            def utility_method():
                return 'stuff'

        # registered like so in ``your_app_bundle/routes.py``
        routes = lambda: [
            controller(SiteController),
        ]

        # results in the following routes
        SiteController.index            => GET /
        SiteController.about            => GET /about

        # but without the @no_route decorator, it would have also added this route:
        SiteController.utility_method   => GET /utility-method

    NOTE: The perhaps more Pythonic way to accomplish this is to make all non-route
    methods protected by prefixing them with an underscore, eg ``_utility_method``.
    """
    def wrapper(fn):
        setattr(fn, NO_ROUTES_ATTR, True)
        return fn

    if callable(arg):
        return wrapper(arg)
    return wrapper


def param_converter(*decorator_args, **decorator_kwargs):
    """
    Convert arguments from the URL and/or query string.

    For parsing arguments from the query string, pass their names as
    keyword argument keys where the value is a lookup (dict, Enum) or callable
    used to convert the query string argument's value::

        @route('/users/<int:id>')
        @param_converter(id=User, foo=str, optional=int)
        def show_user(user, foo, optional=10):
            # GET /users/1?foo=bar
            # calls show_user(user=User.query.get(1), foo='bar')

    It also supports loading SQLAlchemy models from the database. Call with the
    url parameter names as keyword argument keys, their values being the model
    class to convert to.

    Models will be looked up by the url param names. If a url param name
    is prefixed with the snake_cased model name, the prefix will be stripped.
    If a model isn't found, abort with a 404.

    The view function's argument names must match the snake_cased model names.

    For example::

        @route('/users/<int:user_id>/posts/<int:id>')
        @param_converter(user_id=User, id=Post)
        def show_post(user, post):
            # the param converter does the database lookups:
            # user = User.query.get(id=user_id)
            # post = Post.query.get(id=id)
            # and calls the decorated view: show_post(user, post)

        # or to customize the argument names passed to the view:
        @route('/users/<int:user_id>/posts/<int:post_id>')
        @param_converter(user_id={'user_arg_name': User},
                         post_id={'post_arg_name': Post})
        def show_post(user_arg_name, post_arg_name):
            # do stuff
    """
    def wrapped(fn):
        @wraps(fn)
        def decorated(*view_args, **view_kwargs):
            if Model is not None:
                view_kwargs = _convert_models(view_kwargs, decorator_kwargs)
            view_kwargs = _convert_query_params(view_kwargs, decorator_kwargs)
            return fn(*view_args, **view_kwargs)
        return decorated

    if decorator_args and callable(decorator_args[0]):
        return wrapped(decorator_args[0])
    return wrapped


def _convert_models(view_kwargs: dict,
                    url_param_names_to_models: dict,
                    ) -> dict:
    for url_param_name, model_mapping in url_param_names_to_models.items():
        if url_param_name not in view_kwargs and url_param_name not in request.args:
            continue

        arg_name = None
        model = model_mapping
        if isinstance(model_mapping, dict):
            arg_name, model = list(model_mapping.items())[0]

        if not (isinstance(model, type) and issubclass(model, Model)):
            continue

        if not arg_name:
            arg_name = snake_case(model.__name__)

        filter_by = url_param_name.replace(
            snake_case(model.__name__) + '_', '')
        instance = model.query.filter_by(**{
            filter_by: view_kwargs.pop(url_param_name, request.args.get(url_param_name)),
        }).first()

        if not instance:
            abort(HTTPStatus.NOT_FOUND)

        view_kwargs[arg_name] = instance

    return view_kwargs


def _convert_query_params(view_kwargs: dict,
                          param_name_to_converters: dict,
                          ) -> dict:
    for name, converter in param_name_to_converters.items():
        is_model_converter = isinstance(converter, type) and issubclass(converter, Model)
        if is_model_converter or name not in request.args:
            continue

        value = request.args.getlist(name)
        if len(value) == 1:
            value = value[0]

        if isinstance(converter, (dict, Enum)):
            value = converter[value]
        elif callable(converter):
            value = converter(value)
        view_kwargs[name] = value

    return view_kwargs


__all__ = [
    'no_route',
    'param_converter',
    'route',
]
