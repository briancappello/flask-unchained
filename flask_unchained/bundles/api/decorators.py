from functools import wraps
from http import HTTPStatus

from flask import abort

from .utils import safe_load


def list_loader(*decorator_args, model):
    """
    Decorator to automatically query the database for all records of a model.

    :param model: The model class to query
    """
    def wrapped(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            return fn(model.query.all())
        return decorated

    if decorator_args and callable(decorator_args[0]):
        return wrapped(decorator_args[0])
    return wrapped


def patch_loader(*decorator_args, serializer):
    """
    Decorator to automatically load and (partially) update a model from json
    request data

    :param serializer: The ModelSerializer to use to load data from the request
    """
    def wrapped(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            result = safe_load(serializer, instance=kwargs.pop('instance'),
                               partial=True)
            if not result.errors and not result.data.id:
                abort(HTTPStatus.NOT_FOUND)
            return fn(*result)
        return decorated

    if decorator_args and callable(decorator_args[0]):
        return wrapped(decorator_args[0])
    return wrapped


def put_loader(*decorator_args, serializer):
    """
    Decorator to automatically load and update a model from json request data

    :param serializer: The ModelSerializer to use to load data from the request
    """
    def wrapped(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            result = safe_load(serializer, instance=kwargs.pop('instance'))
            if not result.errors and not result.data.id:
                abort(HTTPStatus.NOT_FOUND)
            return fn(*result)
        return decorated

    if decorator_args and callable(decorator_args[0]):
        return wrapped(decorator_args[0])
    return wrapped


def post_loader(*decorator_args, serializer):
    """
    Decorator to automatically instantiate a model from json request data

    :param serializer: The ModelSerializer to use to load data from the request
    """
    def wrapped(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            return fn(*safe_load(serializer))
        return decorated

    if decorator_args and callable(decorator_args[0]):
        return wrapped(decorator_args[0])
    return wrapped
