import inspect

from flask import jsonify, make_response
from flask_unchained import Resource, route
from flask_unchained.bundles.controller.attr_constants import (
    ABSTRACT_ATTR, CONTROLLER_ROUTES_ATTR, FN_ROUTES_ATTR)
from flask_unchained import (
    ALL_METHODS, INDEX_METHODS, MEMBER_METHODS,
    CREATE, DELETE, GET, LIST, PATCH, PUT)
from flask_unchained.bundles.controller.metaclasses import ResourceMeta
from flask_unchained.bundles.controller.route import Route
from flask_unchained.bundles.controller.utils import get_param_tuples
from flask_unchained.bundles.sqlalchemy import BaseModel, SessionManager, param_converter
from flask_unchained import unchained, injectable
from flask_unchained.utils import deep_getattr
from functools import partial
from http import HTTPStatus
try:
    from marshmallow import MarshalResult
except ImportError:
    from flask_unchained import OptionalClass as MarshalResult
from types import FunctionType
from typing import *
from werkzeug.wrappers import Response

from .decorators import list_loader, patch_loader, put_loader, post_loader
from .model_serializer import ModelSerializer
from .utils import unpack


class ModelResourceMeta(ResourceMeta):
    def __new__(mcs, name, bases, clsdict):
        if ABSTRACT_ATTR in clsdict:
            return super().__new__(mcs, name, bases, clsdict)

        routes = {}
        include_methods = set(deep_getattr(clsdict, bases, 'include_methods'))
        exclude_methods = set(deep_getattr(clsdict, bases, 'exclude_methods'))
        for method_name in ALL_METHODS:
            if (method_name in exclude_methods
                    or method_name not in include_methods):
                continue

            route = getattr(clsdict.get(method_name), FN_ROUTES_ATTR, [None])[0]
            if not route:
                route = Route(None, deep_getattr(clsdict, bases, method_name))
                route._controller_name = name

            if method_name in INDEX_METHODS:
                rule = '/'
            else:
                rule = deep_getattr(clsdict, bases, 'member_param')
            route.rule = rule
            routes[method_name] = [route]

        cls = super().__new__(mcs, name, bases, clsdict)
        if cls.model is None:
            raise AttributeError(f'{name} is missing the model attribute')
        setattr(cls, CONTROLLER_ROUTES_ATTR, routes)
        return cls


class ModelResource(Resource, metaclass=ModelResourceMeta):
    __abstract__ = True

    # FIXME all of these might be nicer as class Meta attributes (mostly just
    # for consistency with other places, eg model and serializer classes)
    model: Type[BaseModel] = None
    serializer: ModelSerializer = None
    serializer_create: ModelSerializer = None
    serializer_many: ModelSerializer = None

    include_methods: Union[List[str], Set[str], Tuple[str]] = ALL_METHODS
    exclude_methods: Union[List[str], Set[str], Tuple[str]] = set()

    include_decorators: Union[List[str], Set[str], Tuple[str]] = ALL_METHODS
    exclude_decorators: Union[List[str], Set[str], Tuple[str]] = set()
    method_decorators: Union[
        Union[List[FunctionType], Tuple[FunctionType]],
        Dict[str, Union[List[FunctionType], Tuple[FunctionType]]],
    ] = {}

    def __init__(self, session_manager: SessionManager = injectable):
        self.session_manager = session_manager
        if isinstance(self.model, str):
            self.model = unchained.sqlalchemy_bundle.models[self.model]

    @classmethod
    def methods(cls):
        for method in ALL_METHODS:
            if (method in cls.exclude_methods
                    or method not in cls.include_methods):
                continue
            yield method

    # NOTE:
    # docstrings for these default methods must be 2 lines with the ---
    # (otherwise flasgger will shit a brick)

    @route
    def list(self, instances):
        """list models"""
        return instances

    @route
    def create(self, instance, errors):
        if errors:
            return self.errors(errors)
        return self.created(instance)

    @route
    def get(self, instance):
        return instance

    @route
    def patch(self, instance, errors):
        if errors:
            return self.errors(errors)
        return self.updated(instance)

    @route
    def put(self, instance, errors):
        if errors:
            return self.errors(errors)
        return self.updated(instance)

    @route
    def delete(self, instance):
        return self.deleted(instance)

    def created(self, instance, commit=True):
        """
        Convenience method for saving a model (automatically commits it to
        the database and returns the object with an HTTP 201 status code)
        """
        if commit:
            self.session_manager.save(instance, commit=True)
        return instance, HTTPStatus.CREATED

    def deleted(self, instance):
        """
        Convenience method for deleting a model (automatically commits the
        delete to the database and returns with an HTTP 204 status code)
        """
        self.session_manager.delete(instance, commit=True)
        return '', HTTPStatus.NO_CONTENT

    def updated(self, instance):
        """
        Convenience method for updating a model (automatically commits it to
        the database and returns the object with with an HTTP 200 status code)
        """
        self.session_manager.save(instance, commit=True)
        return instance

    def dispatch_request(self, method_name, *view_args, **view_kwargs):
        resp = super().dispatch_request(method_name, *view_args, **view_kwargs)
        rv, code, headers = unpack(resp)
        if isinstance(rv, Response):
            return self.make_response(rv, code, headers)

        if isinstance(rv, MarshalResult):
            rv = rv.errors and rv.errors or rv.data
        elif isinstance(rv, list) and rv and isinstance(rv[0], self.model):
            rv = self.serializer_many.dump(rv).data
        elif isinstance(rv, self.model):
            rv = self.serializer.dump(rv).data

        return self.make_response(rv, code, headers)

    def make_response(self, data, code=200, headers=None):
        headers = headers or {}
        if isinstance(data, Response):
            return make_response(data, code, headers)

        # FIXME need to support ETags
        # see https://github.com/Nobatek/flask-rest-api/blob/master/flask_rest_api/response.py

        # FIXME lookup representations or somehow else handle Accept headers
        return make_response(jsonify(data), code, headers)

    def get_decorators(self, method_name):
        decorators = super().get_decorators(method_name).copy()
        if method_name not in ALL_METHODS:
            return decorators

        if isinstance(self.method_decorators, dict):
            decorators += list(self.method_decorators.get(method_name, []))
        elif isinstance(self.method_decorators, (list, tuple)):
            decorators += list(self.method_decorators)

        if (method_name in self.exclude_decorators
                or method_name not in self.include_decorators):
            return decorators

        if method_name == LIST:
            decorators.append(partial(list_loader, model=self.model))
        elif method_name in MEMBER_METHODS:
            param_name = get_param_tuples(self.member_param)[0][1]
            kw_name = 'instance'  # needed by the patch/put loaders
            # for get/delete, allow subclasses to rename view fn args
            # (the patch/put loaders call view functions with positional args,
            #  so no need to inspect function signatures for them)
            if method_name in {DELETE, GET}:
                sig = inspect.signature(getattr(self, method_name))
                kw_name = list(sig.parameters.keys())[0]
            decorators.append(partial(
                param_converter, **{param_name: {kw_name: self.model}}))

        if method_name == CREATE:
            decorators.append(partial(post_loader,
                                      serializer=self.serializer_create))
        elif method_name == PATCH:
            decorators.append(partial(patch_loader,
                                      serializer=self.serializer))
        elif method_name == PUT:
            decorators.append(partial(put_loader,
                                      serializer=self.serializer))
        return decorators
