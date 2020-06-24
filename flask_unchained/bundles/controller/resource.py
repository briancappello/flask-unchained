from typing import *

from flask_unchained.string_utils import pluralize
from py_meta_utils import McsArgs, MetaOption, _missing

from .attr_constants import CONTROLLER_ROUTES_ATTR, REMOVE_SUFFIXES_ATTR
from .constants import ALL_RESOURCE_METHODS, RESOURCE_INDEX_METHODS
from .constants import CREATE, DELETE, GET, LIST, PATCH, PUT
from .controller import (Controller, ControllerMetaclass, ControllerMetaOptionsFactory,
                         ControllerUrlPrefixMetaOption, _get_remove_suffixes)
from .route import Route
from .utils import controller_name, get_param_tuples


RESOURCE_REMOVE_EXTRA_SUFFIXES = ['MethodView']


class ResourceMetaclass(ControllerMetaclass):
    """
    Metaclass for Resource class
    """
    resource_methods = {LIST: ['GET'], CREATE: ['POST'],
                        GET: ['GET'], PATCH: ['PATCH'],
                        PUT: ['PUT'], DELETE: ['DELETE']}

    def __new__(mcs, name, bases, clsdict):
        cls = super().__new__(mcs, name, bases, clsdict)
        if cls.Meta.abstract:
            setattr(cls, REMOVE_SUFFIXES_ATTR, _get_remove_suffixes(
                name, bases, RESOURCE_REMOVE_EXTRA_SUFFIXES))
            return cls

        controller_routes: Dict[str, List[Route]] = getattr(cls, CONTROLLER_ROUTES_ATTR)
        for method_name in ALL_RESOURCE_METHODS:
            if not clsdict.get(method_name):
                continue
            route = controller_routes.get(method_name)[0]
            rule = None
            if method_name in RESOURCE_INDEX_METHODS:
                rule = '/'
            else:
                route._is_member_method = True
                route._member_param = cls.Meta.member_param
            route.rule = rule
            controller_routes[method_name] = [route]
        setattr(cls, CONTROLLER_ROUTES_ATTR, controller_routes)

        return cls


class ResourceUrlPrefixMetaOption(MetaOption):
    """
    The url prefix to use for all routes from this resource. Defaults to the
    pluralized and snake_cased class name with the ``Resource``, ``MethodView``,
    ``Controller``, and ``View`` suffixes stripped.
    """
    def __init__(self):
        super().__init__('url_prefix', default=_missing, inherit=False)

    def get_value(self, meta, base_classes_meta, mcs_args: McsArgs):
        value = super().get_value(meta, base_classes_meta, mcs_args)
        if value is not _missing:
            return value

        ctrl_name = controller_name(mcs_args.name,
                                    mcs_args.getattr(REMOVE_SUFFIXES_ATTR))
        return '/' + pluralize(ctrl_name.replace('_', '-'))

    def check_value(self,
                    value,
                    mcs_args: McsArgs,  # skipcq: PYL-W0613 (unused arg)
                    ) -> None:
        if not value:
            return

        if not isinstance(value, str):
            raise ValueError(f'The {self.name} meta option must be a string')


class ResourceMemberParamMetaOption(MetaOption):
    """
    The url parameter rule to use for the special member methods (``get``, ``patch``,
    ``put``, and ``delete``) of this resource. Defaults to ``<int:id>``.
    """
    def __init__(self):
        super().__init__('member_param', default=_missing, inherit=True)

    def get_value(self, meta, base_classes_meta, mcs_args: McsArgs):
        value = super().get_value(meta, base_classes_meta, mcs_args)
        if value is not _missing:
            return value

        return '<int:id>'

    def check_value(self, value, mcs_args: McsArgs):
        if mcs_args.is_abstract:
            return

        if not isinstance(value, str) or not len(get_param_tuples(value)) == 1:
            raise TypeError(f'The {self.name} meta option must be in the format of '
                            f'<werkzeug_type:param_name>')


class ResourceUniqueMemberParamMetaOption(MetaOption):
    """
    The url parameter rule to use for the special member methods (``get``, ``patch``,
    ``put``, and ``delete``) of this resource when
    :attr:`~flask_unchained.Resource.Meta.member_param` conflicts with a subresource's
    ``member_param``.
    """
    def __init__(self):
        super().__init__('unique_member_param', default=None, inherit=False)

    # def get_value(...)
    # NOTE: the default value logic lives in `Route.unique_member_param`

    def check_value(self, value, mcs_args: McsArgs):
        if mcs_args.is_abstract or value is None:
            return

        if not isinstance(value, str) or not len(get_param_tuples(value)) == 1:
            raise TypeError(f'The {self.name} meta option must be in the format of '
                            f'<werkzeug_type:param_name>')


class ResourceMetaOptionsFactory(ControllerMetaOptionsFactory):
    _options = [option for option in ControllerMetaOptionsFactory._options
                if not issubclass(option, ControllerUrlPrefixMetaOption)] + [
        ResourceUrlPrefixMetaOption,
        ResourceMemberParamMetaOption,
        ResourceUniqueMemberParamMetaOption,
    ]


class Resource(Controller, metaclass=ResourceMetaclass):
    """
    Base class for resources. This is intended for building RESTful APIs.
    Following the rules shown below, if the given class method is defined,
    this class will automatically set up the shown routing rule for it.

    .. list-table::
       :widths: 15 10 30
       :header-rows: 1

       * - HTTP Method
         - Resource class method name
         - URL Rule
       * - GET
         - list
         - /
       * - POST
         - create
         - /
       * - GET
         - get
         - /<cls.Meta.member_param>
       * - PATCH
         - patch
         - /<cls.Meta.member_param>
       * - PUT
         - put
         - /<cls.Meta.member_param>
       * - DELETE
         - delete
         - /<cls.Meta.member_param>

    So, for example::

        from flask_unchained import Resource, injectable, param_converter
        from flask_unchained.bundles.security import User, UserManager


        class UserResource(Resource):
            class Meta:
                member_param: '<string:username>'

            user_manager: UserManager = injectable

            def list():
                return self.jsonify(dict(users=self.user_manager.all()))
                # NOTE: returning SQLAlchemy models directly like this is
                # only supported by ModelResource from the API Bundle

            def create():
                user = self.user_manager.create(**data, commit=True)
                return self.jsonify(dict(user=user), code=201)

            @param_converter(username=User)
            def get(user):
                return self.jsonify(dict(user=user)

            @param_converter(username=User)
            def patch(user):
                user = self.user_manager.update(user, **data, commit=True)
                return self.jsonify(dict(user=user))

            @param_converter(username=User)
            def put(user):
                user = self.user_manager.update(user, **data, commit=True)
                return self.jsonify(dict(user=user))

            @param_converter(username=User)
            def delete(user):
                self.user_manager.delete(user, commit=True)
                return self.make_response('', code=204)

    Registered like so::

        routes = lambda: [
            resource('/users', UserResource),
        ]

    Would register the following routes::

        GET     /users                      UserResource.list
        POST    /users                      UserResource.create
        GET     /users/<string:username>    UserResource.get
        PATCH   /users/<string:username>    UserResource.patch
        PUT     /users/<string:username>    UserResource.put
        DELETE  /users/<string:username>    UserResource.delete

    See also :class:`~flask_unchained.bundles.api.model_resource.ModelResource` from
    the API bundle.
    """
    _meta_options_factory_class = ResourceMetaOptionsFactory

    class Meta:
        abstract = True

    @classmethod
    def method_as_view(cls, method_name, *class_args, **class_kwargs):
        view = super().method_as_view(method_name, *class_args, **class_kwargs)
        view.methods = cls.resource_methods.get(method_name, None)
        return view


__all__ = [
    'Resource',
    'ResourceMetaclass',
    'ResourceMetaOptionsFactory',
]
