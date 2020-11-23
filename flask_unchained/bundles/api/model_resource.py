import inspect
from typing import *

from flask import current_app, make_response, request
from flask_unchained import Resource, route, param_converter, unchained, injectable
from flask_unchained.string_utils import kebab_case, pluralize
from flask_unchained.bundles.controller.attr_constants import (
    CONTROLLER_ROUTES_ATTR, FN_ROUTES_ATTR)
from flask_unchained.bundles.controller.constants import (
    ALL_RESOURCE_METHODS, RESOURCE_INDEX_METHODS, RESOURCE_MEMBER_METHODS,
    CREATE, DELETE, GET, LIST, PATCH, PUT)
from flask_unchained.bundles.controller.resource import (
    ResourceMetaclass, ResourceMetaOptionsFactory, ResourceUrlPrefixMetaOption)
from flask_unchained.bundles.controller.route import Route
from flask_unchained.bundles.controller.utils import get_param_tuples
from flask_unchained.bundles.sqlalchemy import SessionManager
from flask_unchained.bundles.sqlalchemy.meta_options import ModelMetaOption
from functools import partial
from http import HTTPStatus
from py_meta_utils import McsArgs, MetaOption, _missing
from werkzeug.wrappers import Response

from .decorators import list_loader, patch_loader, put_loader, post_loader
from .model_serializer import ModelSerializer
from .utils import unpack


class ModelResourceMetaclass(ResourceMetaclass):
    def __new__(mcs, name, bases, clsdict):
        mcs_args = McsArgs(mcs, name, bases, clsdict)
        cls = super().__new__(*mcs_args)
        if mcs_args.is_abstract:
            return cls

        routes: Dict[str, List[Route]] = getattr(cls, CONTROLLER_ROUTES_ATTR)
        include_methods = set(cls.Meta.include_methods)
        exclude_methods = set(cls.Meta.exclude_methods)
        for method_name in ALL_RESOURCE_METHODS:
            if (method_name in exclude_methods
                    or method_name not in include_methods):
                routes.pop(method_name, None)
                continue

            route: Route = getattr(clsdict.get(method_name), FN_ROUTES_ATTR, [None])[0]
            if not route:
                route = Route(None, mcs_args.getattr(method_name))

            if method_name in RESOURCE_INDEX_METHODS:
                rule = '/'
            else:
                rule = cls.Meta.member_param
            route.rule = rule
            routes[method_name] = [route]

        setattr(cls, CONTROLLER_ROUTES_ATTR, routes)
        return cls


class ModelResourceSerializerMetaOption(MetaOption):
    """
    The serializer instance to use. If left unspecified, it will be looked up by
    model name and automatically assigned.
    """
    def __init__(self):
        super().__init__('serializer', default=None, inherit=True)

    def check_value(self,
                    value,
                    mcs_args: McsArgs,  # skipcq: PYL-W0613 (unused arg)
                    ) -> None:
        if not value or isinstance(value, ModelSerializer) or (
                isinstance(value, type) and issubclass(value, ModelSerializer)
        ):
            return
        raise ValueError(f'The {self.name} meta option must be a subclass or '
                         f'instance of ModelSerializer')


class ModelResourceSerializerCreateMetaOption(MetaOption):
    """
    The serializer instance to use for creating models. If left unspecified, it
    will be looked up by model name and automatically assigned.
    """
    def __init__(self):
        super().__init__('serializer_create', default=None, inherit=True)

    def check_value(self,
                    value,
                    mcs_args: McsArgs,  # skipcq: PYL-W0613 (unused arg)
                    ) -> None:
        if not value or isinstance(value, ModelSerializer) or (
                isinstance(value, type) and issubclass(value, ModelSerializer)
        ):
            return
        raise ValueError(f'The {self.name} meta option must be a subclass or '
                         f'instance of ModelSerializer')

class ModelResourceSerializerManyMetaOption(MetaOption):
    """
    The serializer instance to use for listing models. If left unspecified, it
    will be looked up by model name and automatically assigned.
    """
    def __init__(self):
        super().__init__('serializer_many', default=None, inherit=True)

    def check_value(self,
                    value,
                    mcs_args: McsArgs,  # skipcq: PYL-W0613 (unused arg)
                    ) -> None:
        if not value or isinstance(value, ModelSerializer) or (
                isinstance(value, type) and issubclass(value, ModelSerializer)
        ):
            return
        raise ValueError(f'The {self.name} meta option must be a subclass or '
                         f'instance of ModelSerializer')


class ModelResourceIncludeMethodsMetaOption(MetaOption):
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

        return ALL_RESOURCE_METHODS

    def check_value(self,
                    value,
                    mcs_args: McsArgs,  # skipcq: PYL-W0613 (unused arg)
                    ) -> None:
        if not value:
            return

        if not all(x in ALL_RESOURCE_METHODS for x in value):
            raise ValueError(f'Invalid values for the {self.name} meta option. The '
                             f'valid values are ' + ', '.join(ALL_RESOURCE_METHODS))


class ModelResourceExcludeMethodsMetaOption(MetaOption):
    """
    A list of resource methods to exclude. Defaults to ``()``.
    """
    def __init__(self):
        super().__init__('exclude_methods', default=(), inherit=True)

    def check_value(self,
                    value,
                    mcs_args: McsArgs,  # skipcq: PYL-W0613 (unused arg)
                    ) -> None:
        if not value:
            return

        if not all(x in ALL_RESOURCE_METHODS for x in value):
            raise ValueError(f'Invalid values for the {self.name} meta option. The '
                             f'valid values are ' + ', '.join(ALL_RESOURCE_METHODS))


class ModelResourceIncludeDecoratorsMetaOption(MetaOption):
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

        return ALL_RESOURCE_METHODS

    def check_value(self,
                    value,
                    mcs_args: McsArgs,  # skipcq: PYL-W0613 (unused arg)
                    ) -> None:
        if not value:
            return

        if not all(x in ALL_RESOURCE_METHODS for x in value):
            raise ValueError(f'Invalid values for the {self.name} meta option. The '
                             f'valid values are ' + ', '.join(ALL_RESOURCE_METHODS))


class ModelResourceExcludeDecoratorsMetaOption(MetaOption):
    """
    A list of resource methods for which to *not* apply the default decorators, as
    outlined in :attr:`include_decorators`. Defaults to ``()``.
    """
    def __init__(self):
        super().__init__('exclude_decorators', default=(), inherit=True)

    def check_value(self,
                    value,
                    mcs_args: McsArgs,  # skipcq: PYL-W0613 (unused arg)
                    ) -> None:
        if not value:
            return

        if not all(x in ALL_RESOURCE_METHODS for x in value):
            raise ValueError(f'Invalid values for the {self.name} meta option. The '
                             f'valid values are ' + ', '.join(ALL_RESOURCE_METHODS))


class ModelResourceMethodDecoratorsMetaOption(MetaOption):
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
            if not all(callable(x) for x in value):
                raise ValueError(f'The {self.name} meta option requires a '
                                 f'list or tuple of callables')
        else:
            for method_name, decorators in value.items():
                if not mcs_args.getattr(method_name):
                    raise ValueError(
                        f'The {method_name} was not found on {mcs_args.name}')
                if not all(callable(x) for x in decorators):
                    raise ValueError(f'Invalid decorator detected in the {self.name} '
                                     f'meta option for the {method_name} key')


class ModelResourceUrlPrefixMetaOption(MetaOption):
    """
    The url prefix to use for all routes from this resource. Defaults to the
    pluralized and snake_cased model class name.
    """
    def __init__(self):
        super().__init__('url_prefix', default=_missing, inherit=False)

    def get_value(self, meta, base_classes_meta, mcs_args: McsArgs):
        value = super().get_value(meta, base_classes_meta, mcs_args)
        if (value is not _missing
                or mcs_args.Meta.abstract
                or not mcs_args.Meta.model):
            return value

        return '/' + pluralize(kebab_case(mcs_args.Meta.model.__name__))

    def check_value(self,
                    value,
                    mcs_args: McsArgs,  # skipcq: PYL-W0613 (unused arg)
                    ) -> None:
        if not value:
            return

        if not isinstance(value, str):
            raise ValueError(f'The {self.name} meta option must be a string')


class ModelResourceMetaOptionsFactory(ResourceMetaOptionsFactory):
    _allowed_properties = ['model']
    _options = [option for option in ResourceMetaOptionsFactory._options
                if not issubclass(option, ResourceUrlPrefixMetaOption)] + [
        ModelMetaOption,
        ModelResourceUrlPrefixMetaOption,  # must come after the model meta option
        ModelResourceSerializerMetaOption,
        ModelResourceSerializerCreateMetaOption,
        ModelResourceSerializerManyMetaOption,
        ModelResourceIncludeMethodsMetaOption,
        ModelResourceExcludeMethodsMetaOption,
        ModelResourceIncludeDecoratorsMetaOption,
        ModelResourceExcludeDecoratorsMetaOption,
        ModelResourceMethodDecoratorsMetaOption,
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


class ModelResource(Resource, metaclass=ModelResourceMetaclass):
    """
    Base class for model resources. This is intended for building RESTful APIs
    with SQLAlchemy models and Marshmallow serializers.
    """
    _meta_options_factory_class = ModelResourceMetaOptionsFactory

    class Meta:
        abstract = True

    session_manager: SessionManager = injectable

    @classmethod
    def methods(cls):
        for method in ALL_RESOURCE_METHODS:
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

        if isinstance(rv, list) and rv and isinstance(rv[0], self.Meta.model):
            rv = self.Meta.serializer_many.dump(rv)
        elif isinstance(rv, self.Meta.model):
            rv = self.Meta.serializer.dump(rv)

        return self.make_response(rv, code, headers)

    def make_response(self, data, code=200, headers=None):  # skipcq:  PYL-W0221
        headers = headers or {}
        if isinstance(data, Response):
            return make_response(data, code, headers)

        # FIXME need to support ETags
        # see https://github.com/Nobatek/flask-rest-api/blob/master/flask_rest_api/response.py

        accept = request.headers.get('Accept', 'application/json')
        try:
            dump_fn = current_app.config.ACCEPT_HANDLERS[accept]
        except KeyError as e:
            # see if we can use JSON when there is no handler for the requested Accept header
            if '*/*' not in accept:
                raise e
            dump_fn = current_app.config.ACCEPT_HANDLERS['application/json']

        return make_response(dump_fn(data), code, headers)

    def get_decorators(self, method_name):
        decorators = list(super().get_decorators(method_name)).copy()
        if method_name not in ALL_RESOURCE_METHODS:
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
        elif method_name in RESOURCE_MEMBER_METHODS:
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
    'ModelResourceMetaclass',
    'ModelResourceMetaOptionsFactory',
]
