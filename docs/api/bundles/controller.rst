Controller Bundle API Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: flask_unchained.bundles.controller.ControllerBundle
   :members:

Config
~~~~~~

.. autoclass:: flask_unchained.bundles.controller.config.Config
   :members:

Controller
~~~~~~~~~~

.. autoclass:: flask_unchained.Controller
   :members:
   :exclude-members: method_as_view

Decorators
~~~~~~~~~~

.. autofunction:: flask_unchained.route
.. autofunction:: flask_unchained.no_route

Hooks
~~~~~

.. automodule:: flask_unchained.bundles.controller.hooks
   :members:

Resource
~~~~~~~~

.. autoclass:: flask_unchained.Resource
   :members:
   :exclude-members: method_as_view

Route
~~~~~

.. automodule:: flask_unchained.bundles.controller.route
   :members:

Routes
~~~~~~

.. autofunction:: flask_unchained.controller
.. autofunction:: flask_unchained.func
.. autofunction:: flask_unchained.get
.. autofunction:: flask_unchained.include
.. autofunction:: flask_unchained.patch
.. autofunction:: flask_unchained.post
.. autofunction:: flask_unchained.prefix
.. autofunction:: flask_unchained.put
.. autofunction:: flask_unchained.resource
.. autofunction:: flask_unchained.rule

Utils
~~~~~

.. autofunction:: flask_unchained.redirect
.. autofunction:: flask_unchained.url_for

.. automodule:: flask_unchained.bundles.controller.utils
   :members:
   :exclude-members: redirect, url_for
