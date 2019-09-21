from functools import wraps
from http import HTTPStatus

from flask import abort, request

try:
    from marshmallow import ValidationError
except ImportError:
    ValidationError = Exception


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
            errors = {}
            try:
                data = serializer.load(request.get_json(),
                                       instance=kwargs.pop('instance'),
                                       partial=True)
            except ValidationError as e:
                errors = e.normalized_messages()
                data = e.valid_data

            if not errors and not data.id:
                abort(HTTPStatus.NOT_FOUND)

            return fn(data, errors)
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
            errors = {}
            try:
                data = serializer.load(request.get_json(),
                                       instance=kwargs.pop('instance'))
            except ValidationError as e:
                data = e.valid_data
                errors = e.normalized_messages()

            if not errors and not data.id:
                abort(HTTPStatus.NOT_FOUND)

            return fn(data, errors)
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
            errors = {}
            try:
                data = serializer.load(request.get_json())
            except ValidationError as e:
                errors = e.normalized_messages()
                data = e.valid_data
            return fn(data, errors)
        return decorated

    if decorator_args and callable(decorator_args[0]):
        return wrapped(decorator_args[0])
    return wrapped
