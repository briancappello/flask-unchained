from flask_unchained.string_utils import pluralize
from py_meta_utils import deep_getattr

from .attr_constants import CONTROLLER_ROUTES_ATTR, REMOVE_SUFFIXES_ATTR
from .constants import ALL_METHODS, INDEX_METHODS
from .constants import CREATE, DELETE, GET, LIST, PATCH, PUT
from .controller import Controller, ControllerMeta, _get_remove_suffixes
from .utils import controller_name


RESOURCE_REMOVE_EXTRA_SUFFIXES = ['MethodView']


class ResourceMeta(ControllerMeta):
    """
    Metaclass for Resource class
    """
    resource_methods = {LIST: ['GET'], CREATE: ['POST'],
                        GET: ['GET'], PATCH: ['PATCH'],
                        PUT: ['PUT'], DELETE: ['DELETE']}

    def __new__(mcs, name, bases, clsdict):
        cls = super().__new__(mcs, name, bases, clsdict)
        if clsdict['_meta'].abstract:
            setattr(cls, REMOVE_SUFFIXES_ATTR, _get_remove_suffixes(
                name, bases, RESOURCE_REMOVE_EXTRA_SUFFIXES))
            return cls

        controller_routes = getattr(cls, CONTROLLER_ROUTES_ATTR)
        for method_name in ALL_METHODS:
            if not clsdict.get(method_name):
                continue
            route = controller_routes.get(method_name)[0]
            rule = None
            if method_name in INDEX_METHODS:
                rule = '/'
            else:
                route._is_member_method = True
                route._member_param = deep_getattr(clsdict, bases, 'member_param')
            route.rule = rule
            controller_routes[method_name] = [route]
        setattr(cls, CONTROLLER_ROUTES_ATTR, controller_routes)

        return cls


class UrlPrefixDescriptor:
    def __get__(self, instance, cls):
        return '/' + pluralize(controller_name(cls).replace('_', '-'))


class Resource(Controller, metaclass=ResourceMeta):
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
         - /<cls.member_param>
       * - PATCH
         - patch
         - /<cls.member_param>
       * - PUT
         - put
         - /<cls.member_param>
       * - DELETE
         - delete
         - /<cls.member_param>

    So, for example::

        from flask_unchained import Resource, injectable, param_converter
        from flask_unchained.bundles.security import User, UserManager


        class UserResource(Resource):
            member_param: '<string:username>'

            def __init__(self, user_manager: UserManager = injectable):
                super().__init__()
                self.user_manager = user_manager

            def list():
                return self.jsonify(dict(users=User.query.all()))

            def create():
                user = self.user_manager.create(**data, commit=True)
                return self.jsonify(dict(user=user), code=201)

            @param_converter(username=User)
            def get(user):
                return self.jsonify(dict( user=user)

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
    class Meta:
        abstract = True

    member_param = '<int:id>'
    """
    The URL parameter to use for member methods (get, patch, put, and delete).
    """

    unique_member_param = None
    """
    The URL parameter to use for member methods (get, patch, put, and delete)
    when there is a conflict with a subresource's member_param.
    """

    url_prefix = UrlPrefixDescriptor()
    """
    The URL prefix to use for this Resource. Defaults to the pluralized,
    kebab-cased controller name (eg UserController => '/users',
                                    FooBarController => '/foo-bars')
    """

    @classmethod
    def method_as_view(cls, method_name, *class_args, **class_kwargs):
        view = super().method_as_view(method_name, *class_args, **class_kwargs)
        view.methods = cls.resource_methods.get(method_name, None)
        return view
