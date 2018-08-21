from flask_unchained.string_utils import pluralize

from .controller import Controller
from .metaclasses import ResourceMeta
from .utils import controller_name


class UrlPrefixDescriptor:
    def __get__(self, instance, cls):
        return '/' + pluralize(controller_name(cls))


class Resource(Controller, metaclass=ResourceMeta):
    """
    Base class for resources. This is intended for building RESTful APIs.
    Following the rules shown below, if the given class method is defined,
    this class will automatically set up the shown routing rule for it.

    .. list-table::
       :widths: 15 10 30
       :header-rows: 1

       * - HTTP Method
         - Rule
         - Resource class method name
       * - GET
         - /
         - list
       * - POST
         - /
         - create
       * - GET
         - /<cls.member_param>
         - get
       * - PATCH
         - /<cls.member_param>
         - patch
       * - PUT
         - /<cls.member_param>
         - put
       * - DELETE
         - /<cls.member_param>
         - delete

    So, for example::

        class UserResource(Resource):
            member_param: '<string:username>'

            def list():
                return self.jsonify(dict(users=User.query.all()))

            def create():
                # create user
                return self.jsonify(dict(user=user), code=201)

            def get(username):
                # get user
                return self.jsonify(dict(user=user))

            def patch(username):
                # update user
                return self.jsonify(dict(user=user))

            def put(username):
                # update user
                return self.jsonify(dict(user=user))

            def delete(username):
                # delete user
                return make_response('', code=204)

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

    __abstract__ = True

    url_prefix = UrlPrefixDescriptor()
    member_param = '<int:id>'

    @classmethod
    def method_as_view(cls, method_name, *class_args, **class_kwargs):
        view = super().method_as_view(method_name, *class_args, **class_kwargs)
        view.methods = cls.resource_methods.get(method_name, None)
        return view
