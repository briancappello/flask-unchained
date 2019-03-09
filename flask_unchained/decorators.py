from enum import Enum
from functools import wraps
from http import HTTPStatus

from flask import abort, request
from flask_unchained.string_utils import snake_case

try:
    from sqlalchemy_unchained import BaseModel as Model
except ImportError:
    Model = None


def param_converter(*decorator_args, **decorator_kwargs):
    """
    Call with the url parameter names as keyword argument keys, their values
    being the model to convert to.

    Models will be looked up by the url param names. If a url param name
    is prefixed with the snake-cased model name, the prefix will be stripped.

    If a model isn't found, abort with a 404.

    The action's argument names must match the snake-cased model names.

    For example::

        @bp.route('/users/<int:user_id>/posts/<int:id>')
        @param_converter(user_id=User, id=Post)
        def show_post(user, post):
            # the param converter does the database lookups:
            # user = User.query.filter_by(id=user_id).first()
            # post = Post.query.filter_by(id=id).first()
            # and calls the decorated action: show_post(user, post)

        # or to customize the argument names passed to the action:
        @bp.route('/users/<int:user_id>/posts/<int:post_id>')
        @param_converter(user_id={'user_arg_name': User},
                         post_id={'post_arg_name': Post})
        def show_post(user_arg_name, post_arg_name):
            # do stuff ...

    Also supports parsing arguments from the query string. For query string
    keyword arguments, use a lookup (dict, Enum) or callable::

        @bp.route('/users/<int:id>')
        @param_converter(id=User, foo=str, optional=int)
        def show_user(user, foo, optional=10):
            # GET /users/1?foo=bar
            # calls show_user(user=User.get(1), foo='bar')
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
    'param_converter',
]
