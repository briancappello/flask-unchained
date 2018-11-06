Flask Unchained
---------------

AppFactory
^^^^^^^^^^

.. autoclass:: flask_unchained.AppFactory
   :members:

BaseService
^^^^^^^^^^^

.. autoclass:: flask_unchained.BaseService
   :members:

Bundle
^^^^^^

.. autoclass:: flask_unchained.Bundle
   :members:

AppBundle
^^^^^^^^^

.. autoclass:: flask_unchained.AppBundle
   :members:

BundleConfig
^^^^^^^^^^^^

.. autoclass:: flask_unchained.BundleConfig
   :members:

AppBundleConfig
^^^^^^^^^^^^^^^

.. autoclass:: flask_unchained.AppBundleConfig
   :members:

FlaskForm
^^^^^^^^^

.. autoclass:: flask_unchained.FlaskForm
   :members:

FlaskUnchained
^^^^^^^^^^^^^^

.. autoclass:: flask_unchained.FlaskUnchained
   :members:

Unchained
^^^^^^^^^

.. autoclass:: flask_unchained.Unchained
   :members:

Constants
^^^^^^^^^

.. automodule:: flask_unchained.constants
   :members:

injectable
~~~~~~~~~~

.. automodule:: flask_unchained.di
   :members: injectable

Hooks
^^^^^

AppFactoryHook
~~~~~~~~~~~~~~

.. autoclass:: flask_unchained.AppFactoryHook
   :members:

ConfigureAppHook
~~~~~~~~~~~~~~~~

.. autoclass:: flask_unchained.hooks.ConfigureAppHook
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: apply_default_config, collect_from_bundle, collect_from_bundles, discover_from_bundle_superclasses, get_bundle_config, get_module_name, import_bundle_module, limit_discovery_to_local_declarations, key_name, process_objects, type_check, update_shell_context

RegisterExtensionsHook
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: flask_unchained.hooks.RegisterExtensionsHook
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: collect_from_bundle, collect_from_bundles, discover_from_bundle_superclasses, get_module_name, import_bundle_module, limit_discovery_to_local_declarations, key_name, process_objects, type_check, update_shell_context, run_hook, get_extension_tuples, resolve_extension_order

InitExtensionsHook
~~~~~~~~~~~~~~~~~~

.. autoclass:: flask_unchained.hooks.InitExtensionsHook
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: collect_from_bundle, collect_from_bundles, discover_from_bundle_superclasses, get_module_name, import_bundle_module, limit_discovery_to_local_declarations, key_name, process_objects, type_check, update_shell_context, run_hook, get_extension_tuples, resolve_extension_order

InjectServicesIntoExtensionsHook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: flask_unchained.hooks.InjectServicesIntoExtensionsHook
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: collect_from_bundle, collect_from_bundles, discover_from_bundle_superclasses, get_module_name, import_bundle_module, limit_discovery_to_local_declarations, key_name, process_objects, type_check, update_shell_context, run_hook

RegisterCommandsHook
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: flask_unchained.hooks.RegisterCommandsHook
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: collect_from_bundle, collect_from_bundles, discover_from_bundle_superclasses, get_module_name, import_bundle_module, limit_discovery_to_local_declarations, key_name, process_objects, type_check, update_shell_context, run_hook, get_bundle_commands, get_bundle_command_groups, is_click_command, is_click_group

RegisterServicesHook
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: flask_unchained.hooks.RegisterServicesHook
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: collect_from_bundle, collect_from_bundles, discover_from_bundle_superclasses, get_module_name, import_bundle_module, limit_discovery_to_local_declarations, key_name, process_objects, type_check, update_shell_context, run_hook

RunHooksHook
~~~~~~~~~~~~

.. autoclass:: flask_unchained.hooks.RunHooksHook
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: collect_from_bundle, collect_from_bundles, discover_from_bundle_superclasses, get_module_name, import_bundle_module, limit_discovery_to_local_declarations, key_name, process_objects, type_check, update_shell_context, run_hook, collect_from_unchained, resolve_hook_order

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

.. autoclass:: flask_unchained.utils.ConfigPropertyMetaclass
   :members:

.. autoclass:: flask_unchained.utils.ConfigProperty
   :members:

Attribute-access Dictionaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: flask_unchained.utils.AttrDict
   :members:
