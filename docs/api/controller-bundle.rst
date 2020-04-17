Controller Bundle API
---------------------

**flask_unchained.bundles.controller**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.controller.ControllerBundle

**flask_unchained.bundles.controller.config**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.controller.config.Config

**flask_unchained.bundles.controller.controller**

.. autosummary::
    :nosignatures:

    ~flask_unchained.Controller

**flask_unchained.bundles.controller.decorators**

.. autosummary::
    :nosignatures:

    ~flask_unchained.param_converter
    ~flask_unchained.route
    ~flask_unchained.no_route

**flask_unchained.bundles.controller.hooks**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.controller.hooks.RegisterBlueprintsHook
    ~flask_unchained.bundles.controller.hooks.RegisterBundleBlueprintsHook
    ~flask_unchained.bundles.controller.hooks.RegisterRoutesHook

**flask_unchained.bundles.controller.resource**

.. autosummary::
    :nosignatures:

    ~flask_unchained.Resource

**flask_unchained.bundles.controller.routes**

.. autosummary::
    :nosignatures:

    ~flask_unchained.controller
    ~flask_unchained.resource
    ~flask_unchained.func
    ~flask_unchained.include
    ~flask_unchained.prefix
    ~flask_unchained.rule
    ~flask_unchained.get
    ~flask_unchained.patch
    ~flask_unchained.post
    ~flask_unchained.put
    ~flask_unchained.delete

**flask_unchained.bundles.controller.utils**

.. autosummary::
    :nosignatures:

    ~flask_unchained.redirect
    ~flask_unchained.url_for
    ~flask_unchained.abort
    ~flask_unchained.generate_csrf

ControllerBundle
^^^^^^^^^^^^^^^^
.. autoclass:: flask_unchained.bundles.controller.ControllerBundle
    :members:

Config
^^^^^^
.. autoclass:: flask_unchained.bundles.controller.config.Config
    :members:
    :undoc-members:

Views
^^^^^

Controller
~~~~~~~~~~
.. autoclass:: flask_unchained.Controller
    :members:

Resource
~~~~~~~~
.. autoclass:: flask_unchained.Resource
    :members:

View Decorators
^^^^^^^^^^^^^^^

param_converter
~~~~~~~~~~~~~~~
.. autofunction:: flask_unchained.param_converter

route
~~~~~
.. autofunction:: flask_unchained.route

no_route
~~~~~~~~
.. autofunction:: flask_unchained.no_route

Declarative Routing
^^^^^^^^^^^^^^^^^^^

controller
~~~~~~~~~~
.. autofunction:: flask_unchained.controller

resource
~~~~~~~~
.. autofunction:: flask_unchained.resource

func
~~~~
.. autofunction:: flask_unchained.func

include
~~~~~~~
.. autofunction:: flask_unchained.include

prefix
~~~~~~
.. autofunction:: flask_unchained.prefix

rule
~~~~
.. autofunction:: flask_unchained.rule

get
~~~
.. autofunction:: flask_unchained.get

patch
~~~~~
.. autofunction:: flask_unchained.patch

post
~~~~
.. autofunction:: flask_unchained.post

put
~~~
.. autofunction:: flask_unchained.put

delete
~~~~~~
.. autofunction:: flask_unchained.delete

Hooks
^^^^^

RegisterBlueprintsHook
~~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.controller.hooks.RegisterBlueprintsHook
    :members:

RegisterBundleBlueprintsHook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.controller.hooks.RegisterBundleBlueprintsHook
    :members:

RegisterRoutesHook
~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.controller.hooks.RegisterRoutesHook
    :members:

FlaskForm
^^^^^^^^^

Using forms in Flask Unchained is exactly the same as it is with `Flask-WTF <https://flask-wtf.readthedocs.io/en/stable/>`_.

.. autoclass:: flask_unchained.FlaskForm
   :members:

Utility Functions
^^^^^^^^^^^^^^^^^

redirect
~~~~~~~~
.. autofunction:: flask_unchained.redirect

url_for
~~~~~~~
.. autofunction:: flask_unchained.url_for

abort
~~~~~
.. autofunction:: flask_unchained.abort

generate_csrf
~~~~~~~~~~~~~
.. autofunction:: flask_unchained.generate_csrf
