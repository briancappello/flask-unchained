import inspect

from flask import jsonify, make_response
from flask_unchained import Resource, route, param_converter, unchained, injectable
from flask_unchained.bundles.controller.attr_constants import (
    CONTROLLER_ROUTES_ATTR, FN_ROUTES_ATTR)
from flask_unchained import (
    ALL_METHODS, INDEX_METHODS, MEMBER_METHODS,
    CREATE, DELETE, GET, LIST, PATCH, PUT)
from flask_unchained.bundles.controller.resource import (
    _ResourceMetaclass, _ResourceMetaOptionsFactory)
from flask_unchained.bundles.controller.route import Route
from flask_unchained.bundles.controller.utils import get_param_tuples
from flask_unchained.bundles.sqlalchemy import SessionManager
from flask_unchained.bundles.sqlalchemy.meta_options import (
    ModelMetaOption as _ModelResourceModelMetaOption)
from functools import partial
from http import HTTPStatus
from py_meta_utils import McsArgs, MetaOption, _missing
from werkzeug.wrappers import Response

try:
    from marshmallow import MarshalResult
except ImportError:
    from py_meta_utils import OptionalClass as MarshalResult

from .decorators import list_loader, patch_loader, put_loader, post_loader
from .model_serializer import ModelSerializer
from .utils import unpack


class _ModelResourceMetaclass(_ResourceMetaclass):
    def __new__(mcs, name, bases, clsdict):
        mcs_args = McsArgs(mcs, name, bases, clsdict)
        if mcs_args.is_abstract:
            return super().__new__(*mcs_args)

        cls = super().__new__(*mcs_args)
        routes = {}
        include_methods = set(cls.Meta.include_methods)
        exclude_methods = set(cls.Meta.exclude_methods)
        for method_name in ALL_METHODS:
            if (method_name in exclude_methods
                    or method_name not in include_methods):
                continue

            route = getattr(clsdict.get(method_name), FN_ROUTES_ATTR, [None])[0]
            if not route:
                route = Route(None, mcs_args.getattr(method_name))

            if method_name in INDEX_METHODS:
                rule = '/'
            else:
                rule = cls.Meta.member_param
            route.rule = rule
            routes[method_name] = [route]

        setattr(cls, CONTROLLER_ROUTES_ATTR, routes)
        return cls


class _ModelResourceSerializerMetaOption(MetaOption):
    """
    The serializer instance to use. If left unspecified, it will be looked up by
    model name and automatically assigned.
    """
    def __init__(self):
        super().__init__('serializer', default=None, inherit=True)

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        assert isinstance(value, ModelSerializer), \
            f'The {self.name} meta option must be an instance of ModelSerializer'


class _ModelResourceSerializerCreateMetaOption(MetaOption):
    """
    The serializer instance to use for creating models. If left unspecified, it
    will be looked up by model name and automatically assigned.
    """
    def __init__(self):
        super().__init__('serializer_create', default=None, inherit=True)

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        assert isinstance(value, ModelSerializer), \
            f'The {self.name} meta option must be an instance of ModelSerializer'


class _ModelResourceSerializerManyMetaOption(MetaOption):
    """
    The serializer instance to use for listing models. If left unspecified, it
    will be looked up by model name and automatically assigned.
    """
    def __init__(self):
        super().__init__('serializer_many', default=None, inherit=True)

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        assert isinstance(value, ModelSerializer), \
            f'The {self.name} meta option must be an instance of ModelSerializer'


class _ModelResourceIncludeMethodsMetaOption(MetaOption):
    """
    A list of resource methods to automatically include. Defaults to
    ``('list', 'create', 'get', 'patch', 'put', 'delete')``.
    """
    def __init__(self):
        super().__init__('include_methods', default=_missing, inherit=True)

    def get_value(self, meta, base_classes_meta, mcs_args: McsArgs):
        value = super().get_value(meta, base_classes_meta, mcs_args)
        if value is not _missing:
            return value

        return ALL_METHODS

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        assert all(x in ALL_METHODS for x in value), \
            f'Invalid values for the {self.name} meta option. The valid values ' \
            f'are ' + ', '.join(ALL_METHODS)


class _ModelResourceExcludeMethodsMetaOption(MetaOption):
    """
    A list of resource methods to exclude. Defaults to ``()``.
    """
    def __init__(self):
        super().__init__('exclude_methods', default=(), inherit=True)

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        assert all(x in ALL_METHODS for x in value), \
            f'Invalid values for the {self.name} meta option. The valid values ' \
            f'are ' + ', '.join(ALL_METHODS)


class _ModelResourceIncludeDecoratorsMetaOption(MetaOption):
    """
    A list of resource methods for which to automatically apply the default decorators.
    Defaults to ``('list', 'create', 'get', 'patch', 'put', 'delete')``.

    .. list-table::
        :widths: 10 30
        :header-rows: 1

        * - Method Name
          - Decorator(s)
        * - list
          - :func:`~flask_unchained.bundles.api.decorators.list_loader`
        * - create
          - :func:`~flask_unchained.bundles.api.decorators.post_loader`
        * - get
          - :func:`~flask_unchained.decorators.param_converter`
        * - patch
          - :func:`~flask_unchained.decorators.param_converter`,
            :func:`~flask_unchained.bundles.api.decorators.patch_loader`
        * - put
          - :func:`~flask_unchained.decorators.param_converter`,
            :func:`~flask_unchained.bundles.api.decorators.put_loader`
        * - delete
          - :func:`~flask_unchained.decorators.param_converter`
    """
    def __init__(self):
        super().__init__('include_decorators', default=_missing, inherit=True)

    def get_value(self, meta, base_classes_meta, mcs_args: McsArgs):
        value = super().get_value(meta, base_classes_meta, mcs_args)
        if value is not _missing:
            return value

        return ALL_METHODS

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        assert all(x in ALL_METHODS for x in value), \
            f'Invalid values for the {self.name} meta option. The valid values ' \
            f'are ' + ', '.join(ALL_METHODS)


class _ModelResourceExcludeDecoratorsMetaOption(MetaOption):
    """
    A list of resource methods for which to *not* apply the default decorators, as
    outlined in :attr:`include_decorators`. Defaults to ``()``.
    """
    def __init__(self):
        super().__init__('exclude_decorators', default=(), inherit=True)

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        assert all(x in ALL_METHODS for x in value), \
            f'Invalid values for the {self.name} meta option. The valid values ' \
            f'are ' + ', '.join(ALL_METHODS)


class _ModelResourceMethodDecoratorsMetaOption(MetaOption):
    """
    This can either be a list of decorators to apply to *all* methods, or a
    dictionary of method names to a list of decorators to apply for each method.
    In both cases, decorators specified here are run *before* the default
    decorators.
    """
    def __init__(self):
        super().__init__('method_decorators', default=(), inherit=True)

    def check_value(self, value, mcs_args: McsArgs):
        if not value:
            return

        if isinstance(value, (list, tuple)):
            assert all(callable(x) for x in value), \
                f'The {self.name} meta option requires a list or tuple of callables'
        else:
            for method_name, decorators in value.items():
                assert mcs_args.getattr(method_name), \
                    f'The {method_name} was not found on {mcs_args.name}'
                assert all(callable(x) for x in decorators), \
                    f'Invalid decorator detected in the {self.name} meta option for ' \
                    f'the {method_name} key'


class _ModelResourceMetaOptionsFactory(_ResourceMetaOptionsFactory):
    _allowed_properties = ['model']
    _options = _ResourceMetaOptionsFactory._options + [
        _ModelResourceModelMetaOption,
        _ModelResourceSerializerMetaOption,
        _ModelResourceSerializerCreateMetaOption,
        _ModelResourceSerializerManyMetaOption,
        _ModelResourceIncludeMethodsMetaOption,
        _ModelResourceExcludeMethodsMetaOption,
        _ModelResourceIncludeDecoratorsMetaOption,
        _ModelResourceExcludeDecoratorsMetaOption,
        _ModelResourceMethodDecoratorsMetaOption,
    ]

    def __init__(self):
        super().__init__()
        self._model = None

    @property
    def model(self):
        # make sure to always return the correct mapped model class
        if not unchained._models_initialized or not self._model:
            return self._model
        return unchained.sqlalchemy_bundle.models[self._model.__name__]

    @model.setter
    def model(self, model):
        self._model = model


class ModelResource(Resource, metaclass=_ModelResourceMetaclass):
    """
    Base class for model resources. This is intended for building RESTful APIs
    with SQLAlchemy models and Marshmallow serializers.
    """
    _meta_options_factory_class = _ModelResourceMetaOptionsFactory

    class Meta:
        abstract = True

    def __init__(self, session_manager: SessionManager = injectable):
        self.session_manager = session_manager

    @classmethod
    def methods(cls):
        for method in ALL_METHODS:
            if (method in cls.Meta.exclude_methods
                    or method not in cls.Meta.include_methods):
                continue
            yield method

    @route
    def list(self, instances):
        """
        List model instances.

        :param instances: The list of model instances.
        :return: The list of model instances.
        """
        return instances

    @route
    def create(self, instance, errors):
        """
        Create an instance of a model.

        :param instance: The created model instance.
        :param errors: Any errors.
        :return: The created model instance, or a dictionary of errors.
        """
        if errors:
            return self.errors(errors)
        return self.created(instance)

    @route
    def get(self, instance):
        """
        Get an instance of a model.

        :param instance: The model instance.
        :return: The model instance.
        """
        return instance

    @route
    def patch(self, instance, errors):
        """
        Partially update a model instance.

        :param instance: The model instance.
        :param errors: Any errors.
        :return: The updated model instance, or a dictionary of errors.
        """
        if errors:
            return self.errors(errors)
        return self.updated(instance)

    @route
    def put(self, instance, errors):
        """
        Update a model instance.

        :param instance: The model instance.
        :param errors: Any errors.
        :return: The updated model instance, or a dictionary of errors.
        """
        if errors:
            return self.errors(errors)
        return self.updated(instance)

    @route
    def delete(self, instance):
        """
        Delete a model instance.

        :param instance: The model instance.
        :return: HTTPStatus.NO_CONTENT
        """
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
        elif isinstance(rv, list) and rv and isinstance(rv[0], self.Meta.model):
            rv = self.Meta.serializer_many.dump(rv).data
        elif isinstance(rv, self.Meta.model):
            rv = self.Meta.serializer.dump(rv).data

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

        if isinstance(self.Meta.method_decorators, dict):
            decorators += list(self.Meta.method_decorators.get(method_name, []))
        elif isinstance(self.Meta.method_decorators, (list, tuple)):
            decorators += list(self.Meta.method_decorators)

        if (method_name in self.Meta.exclude_decorators
                or method_name not in self.Meta.include_decorators):
            return decorators

        if method_name == LIST:
            decorators.append(partial(list_loader, model=self.Meta.model))
        elif method_name in MEMBER_METHODS:
            param_name = get_param_tuples(self.Meta.member_param)[0][1]
            kw_name = 'instance'  # needed by the patch/put loaders
            # for get/delete, allow subclasses to rename view fn args
            # (the patch/put loaders call view functions with positional args,
            #  so no need to inspect function signatures for them)
            if method_name in {DELETE, GET}:
                sig = inspect.signature(getattr(self, method_name))
                kw_name = list(sig.parameters.keys())[0]
            decorators.append(partial(
                param_converter, **{param_name: {kw_name: self.Meta.model}}))

        if method_name == CREATE:
            decorators.append(partial(post_loader,
                                      serializer=self.Meta.serializer_create))
        elif method_name == PATCH:
            decorators.append(partial(patch_loader,
                                      serializer=self.Meta.serializer))
        elif method_name == PUT:
            decorators.append(partial(put_loader,
                                      serializer=self.Meta.serializer))
        return decorators


__all__ = [
    'ModelResource',
]
