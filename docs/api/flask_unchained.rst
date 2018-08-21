Flask Unchained
---------------

AppConfig
^^^^^^^^^

.. automodule:: flask_unchained.app_config
   :members:

AppFactory
^^^^^^^^^^

.. automodule:: flask_unchained.app_factory
   :members:

Bundle
^^^^^^

.. autoclass:: flask_unchained.bundle.Bundle
   :members:

FlaskForm
^^^^^^^^^

.. autoclass:: flask_unchained.forms.flask_form.FlaskForm
   :members:

FlaskUnchained
^^^^^^^^^^^^^^

.. autoclass:: flask_unchained.flask_unchained.FlaskUnchained
   :members:

Unchained
^^^^^^^^^

.. autoclass:: flask_unchained.unchained.Unchained
   :members:

.. FIXME the docs for hooks are all messed up

Hooks
^^^^^

AppFactoryHook
~~~~~~~~~~~~~~

.. autoclass:: flask_unchained.app_factory_hook.AppFactoryHook
   :members: run_hook, process_objects, collect_from_bundles, collect_from_bundle, key_name, type_check, import_bundle_module, get_module_name, update_shell_context
   :member-order: run_hook, process_objects, collect_from_bundles, collect_from_bundle, key_name, type_check, import_bundle_module, get_module_name, update_shell_context

ConfigureAppHook
~~~~~~~~~~~~~~~~

.. autoclass:: flask_unchained.hooks.configure_app_hook.ConfigureAppHook
   :members: bundle_module_name, run_before, run_after, run_hook, apply_default_config, get_config
   :inherited-members: bundle_override_module_name_attr

RegisterExtensionsHook
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: flask_unchained.hooks.register_extensions_hook.RegisterExtensionsHook
   :inherited-members: bundle_override_module_name_attr
   :undoc-members: bundle_module_name, run_before, run_after

InitExtensionsHook
~~~~~~~~~~~~~~~~~~

.. automodule:: flask_unchained.hooks.init_extensions_hook
   :members: InitExtensionsHook
   :inherited-members: bundle_override_module_name_attr
   :undoc-members: bundle_module_name, run_before, run_after

InjectServicesIntoExtensionsHook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: flask_unchained.hooks.inject_services_into_extensions_hook
   :members: InjectServicesIntoExtensions
   :inherited-members: bundle_override_module_name_attr
   :undoc-members: bundle_module_name, run_before, run_after

RegisterCommandsHook
~~~~~~~~~~~~~~~~~~~~

.. automodule:: flask_unchained.hooks.register_commands_hook
   :members: RegisterCommandsHook
   :inherited-members: bundle_override_module_name_attr
   :undoc-members: bundle_module_name, run_before, run_after

RegisterServicesHook
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: flask_unchained.hooks.register_services_hook.RegisterServicesHook
   :members:
   :inherited-members: bundle_override_module_name_attr
   :undoc-members: bundle_module_name, run_before, run_after

RunHooksHook
~~~~~~~~~~~~

.. automodule:: flask_unchained.hooks.run_hooks_hook
   :members: RunHooksHook
   :inherited-members: bundle_override_module_name_attr
   :undoc-members: bundle_module_name, run_before, run_after

Utilities
^^^^^^^^^

Date Utilities
~~~~~~~~~~~~~~

.. autofunction:: flask_unchained.utils.utcnow

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: flask_unchained.utils.get_boolean_env

String Utilities
~~~~~~~~~~~~~~~~

.. automodule:: flask_unchained.string_utils
   :members:

.. autofunction:: flask_unchained.clips_pattern.pluralize
.. autofunction:: flask_unchained.clips_pattern.singularize
.. autofunction:: flask_unchained.utils.format_docstring

Extension Development Utilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: flask_unchained.utils.ConfigPropertyMeta
   :members:

.. autoclass:: flask_unchained.utils.ConfigProperty
   :members:

Metaclass Utilities
~~~~~~~~~~~~~~~~~~~

.. autofunction:: flask_unchained.utils.deep_getattr

Subclassing Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: flask_unchained.utils.OptionalMetaclass
   :members:

.. autoclass:: flask_unchained.utils.OptionalClass
   :members:

Attribute-access Dictionaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: flask_unchained.utils.AttrDict
   :members:
