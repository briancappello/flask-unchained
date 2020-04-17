Flask Unchained API
-------------------

**flask_unchained.app_factory**

.. autosummary::
    :nosignatures:

    ~flask_unchained.AppFactory

**flask_unchained.app_factory_hook**

.. autosummary::
    :nosignatures:

    ~flask_unchained.AppFactoryHook

**flask_unchained.bundles**

.. autosummary::
    :nosignatures:

    ~flask_unchained.AppBundle
    ~flask_unchained.Bundle

**flask_unchained.config**

.. autosummary::
    :nosignatures:

    ~flask_unchained.BundleConfig

**flask_unchained.di**

.. autosummary::
    :nosignatures:

    ~flask_unchained.Service

**flask_unchained.flask_unchained**

.. autosummary::
    :nosignatures:

    ~flask_unchained.FlaskUnchained

**flask_unchained.forms**

.. autosummary::
    :nosignatures:

    ~flask_unchained.FlaskForm

**flask_unchained.hooks**

.. autosummary::
    :nosignatures:

    ~flask_unchained.hooks.ConfigureAppHook
    ~flask_unchained.hooks.InitExtensionsHook
    ~flask_unchained.hooks.RegisterCommandsHook
    ~flask_unchained.hooks.RegisterExtensionsHook
    ~flask_unchained.hooks.RegisterServicesHook
    ~flask_unchained.hooks.RunHooksHook
    ~flask_unchained.hooks.ViewsHook

**flask_unchained.string_utils**

.. autosummary::

    ~flask_unchained.string_utils.right_replace
    ~flask_unchained.string_utils.slugify
    ~flask_unchained.string_utils.pluralize
    ~flask_unchained.string_utils.singularize
    ~flask_unchained.string_utils.camel_case
    ~flask_unchained.string_utils.class_case
    ~flask_unchained.string_utils.kebab_case
    ~flask_unchained.string_utils.snake_case
    ~flask_unchained.string_utils.title_case

**flask_unchained.unchained**

.. autosummary::
    :nosignatures:

    ~flask_unchained.Unchained

**flask_unchained.utils**

.. autosummary::
    :nosignatures:

    ~flask_unchained.utils.AttrDict
    ~flask_unchained.utils.ConfigProperty
    ~flask_unchained.utils.ConfigPropertyMetaclass

.. autosummary::

    ~flask_unchained.utils.cwd_import
    ~flask_unchained.utils.get_boolean_env
    ~flask_unchained.utils.safe_import_module
    ~flask_unchained.utils.utcnow

Constants
^^^^^^^^^
.. automodule:: flask_unchained.constants
   :members:

injectable
~~~~~~~~~~
.. automodule:: flask_unchained.di
   :members: injectable

AppFactory
^^^^^^^^^^
.. autoclass:: flask_unchained.AppFactory
   :members:

AppFactoryHook
^^^^^^^^^^^^^^
.. autoclass:: flask_unchained.AppFactoryHook
   :members:

AppBundle
^^^^^^^^^
.. autoclass:: flask_unchained.AppBundle
    :members:

Bundle
^^^^^^
.. autoclass:: flask_unchained.Bundle
   :members:

BundleConfig
^^^^^^^^^^^^
.. autoclass:: flask_unchained.BundleConfig
   :members:

FlaskUnchained
^^^^^^^^^^^^^^
.. autoclass:: flask_unchained.FlaskUnchained
   :members:

Service
^^^^^^^
.. autoclass:: flask_unchained.Service
   :members:

Hooks
^^^^^

ConfigureAppHook
~~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.hooks.ConfigureAppHook
   :members:

InitExtensionsHook
~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.hooks.InitExtensionsHook
   :members:

RegisterCommandsHook
~~~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.hooks.RegisterCommandsHook
   :members:

RegisterExtensionsHook
~~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.hooks.RegisterExtensionsHook
   :members:

RegisterServicesHook
~~~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.hooks.RegisterServicesHook
   :members:

RunHooksHook
~~~~~~~~~~~~
.. autoclass:: flask_unchained.hooks.RunHooksHook
   :members:

ViewsHook
~~~~~~~~~
.. autoclass:: flask_unchained.hooks.ViewsHook
   :members:

Unchained
^^^^^^^^^
.. autoclass:: flask_unchained.Unchained
   :members:

string_utils
^^^^^^^^^^^^
.. autofunction:: flask_unchained.string_utils.right_replace
.. autofunction:: flask_unchained.string_utils.slugify
.. autofunction:: flask_unchained.string_utils.pluralize
.. autofunction:: flask_unchained.string_utils.singularize
.. autofunction:: flask_unchained.string_utils.camel_case
.. autofunction:: flask_unchained.string_utils.class_case
.. autofunction:: flask_unchained.string_utils.kebab_case
.. autofunction:: flask_unchained.string_utils.snake_case
.. autofunction:: flask_unchained.string_utils.title_case

utils
^^^^^
.. autoclass:: flask_unchained.utils.AttrDict
.. autoclass:: flask_unchained.utils.ConfigProperty
.. autoclass:: flask_unchained.utils.ConfigPropertyMetaclass
.. autofunction:: flask_unchained.utils.cwd_import
.. autofunction:: flask_unchained.utils.get_boolean_env
.. autofunction:: flask_unchained.utils.safe_import_module
.. autofunction:: flask_unchained.utils.utcnow
