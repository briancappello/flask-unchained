Dependency Injection and Services
---------------------------------

Flask Unchained supports dependency injection of services and extensions (by default). Here a "service" means any subclass of :class:`~flask_unchained.BaseService` that lives in a bundle's ``services`` module (or that gets imported there). You can however manually register anything as a "service", even plain values if you really wanted to, using :meth:`flask_unchained.Unchained.register_service`::

   from flask_unchained import unchained

   A_CONST = 'a constant'

   class SomethingNotExtendingBaseService:
       pass

   unchained.register_service('something', SomethingNotExtendingBaseService)
   unchained.register_service('A_CONST', A_CONST)

Services can request other services be injected into them, and as long as there are no circular dependencies, it will work::

   from flask_unchained import BaseService, injectable

   class OneService(BaseService):
       pass

   class TwoService(BaseService):
       one_service: OneService = injectable

By setting the default value of a class attribute or function/method argument to the :attr:`flask_unchained.injectable` constant, you are informing the :class:`~flask_unchained.Unchained` extension that it should inject those arguments.

**IMPORTANT:** The names of services must be unique across *all* of the bundles in your app (by default services are named as the snake-cased class name). If there are any conflicting class names then you will need to use :meth:`flask_unchained.Unchained.service` or :meth:`flask_unchained.Unchained.register_service` to customize the name the service gets registered under::

   from flask_unchained import BaseService, unchained

   @unchained.service('a_unique_name')
   class ServiceWithNameConflict(BaseService):
       pass

Automatic Dependency Injection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Dependency injection is automatically set up on all classes extending :class:`~flask_unchained.BaseService` and :class:`~flask_unchained.Controller`. Here's an example of declaring services to be injected in the constructor::

   from flask_unchained import Controller, injectable
   from flask_unchained.bundles.security import Security, SecurityService, SecurityUtilsService
   from flask_unchained.bundles.sqlalchemy import SessionManager

   class SecurityController(Controller):
       def __init__(self,
                    security: Security = injectable,
                    security_service: SecurityService = injectable,
                    security_utils_service: SecurityUtilsService = injectable,
                    session_manager: SessionManager = injectable):
           self.security = security
           self.security_service = security_service
           self.security_utils_service = security_utils_service
           self.session_manager = session_manager

And here's what the same thing looks like using class attributes::

   from flask_unchained import Controller, injectable
   from flask_unchained.bundles.security import Security, SecurityService, SecurityUtilsService
   from flask_unchained.bundles.sqlalchemy import SessionManager

   class SecurityController(Controller):
       security: Security = injectable
       security_service: SecurityService = injectable
       security_utils_service: SecurityUtilsService = injectable
       session_manager: SessionManager = injectable

Using class attributes is functionally equivalent, but a lot less typing, and is therefore the recommended way of declaring what to inject into classes.

Manual Dependency Injection
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can use the :meth:`flask_unchained.Unchained.inject` decorator anywhere else you want to inject something::

   from flask_unchained import unchained, injectable

   @unchained.inject()
   def a_function(some_service: SomeService = injectable):
       pass

   @unchained.inject()
   class Foobar:
       some_service: SomeService = injectable

Injecting Services into Extensions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It's also possible to inject services into extension instances, however because extensions get initialized before services are registered and initialized, you *cannot* use the inject decorator as described above. Instead, extensions may define a method named ``inject_services``::

   class SweetExtension:
       def init_app(app):
           # injected services are *not* available at this point

       def inject_services(self,
                           one_service: OneService = injectable,
                           two_service: TwoService = injectable):
           self.one_service = one_service
           self.two_service = two_service

This method is optional; if you don't need anything injected into your extension, then you don't need to implement it.
