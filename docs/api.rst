API Documentation
=================

AppConfig
---------

.. automodule:: flask_unchained.app_config
   :members:

AppFactory
----------

.. automodule:: flask_unchained.app_factory
   :members:

Bundle
------

.. automodule:: flask_unchained.bundle
   :members:

Hooks
-----

AppFactoryHook
^^^^^^^^^^^^^^

.. autoclass:: flask_unchained.app_factory_hook.AppFactoryHook
   :members: run_hook, process_objects, collect_from_bundles, collect_from_bundle, key_name, type_check, import_bundle_module, get_module_name, update_shell_context
   :member-order: run_hook, process_objects, collect_from_bundles, collect_from_bundle, key_name, type_check, import_bundle_module, get_module_name, update_shell_context

ConfigureAppHook
^^^^^^^^^^^^^^^^

.. autoclass:: flask_unchained.hooks.configure_app_hook.ConfigureAppHook
   :members: bundle_module_name, run_before, run_after, run_hook, apply_default_config, get_config
   :inherited-members: bundle_override_module_name_attr

RegisterExtensionsHook
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: flask_unchained.hooks.register_extensions_hook.RegisterExtensionsHook
   :inherited-members: bundle_override_module_name_attr
   :undoc-members: bundle_module_name, run_before, run_after

InitExtensionsHook
^^^^^^^^^^^^^^^^^^

.. automodule:: flask_unchained.hooks.init_extensions_hook
   :members: InitExtensionsHook
   :inherited-members: bundle_override_module_name_attr
   :undoc-members: bundle_module_name, run_before, run_after

InjectServicesIntoExtensionsHook
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: flask_unchained.hooks.inject_services_into_extensions_hook
   :members: InjectServicesIntoExtensions
   :inherited-members: bundle_override_module_name_attr
   :undoc-members: bundle_module_name, run_before, run_after

RegisterCommandsHook
^^^^^^^^^^^^^^^^^^^^

.. automodule:: flask_unchained.hooks.register_commands_hook
   :members: RegisterCommandsHook
   :inherited-members: bundle_override_module_name_attr
   :undoc-members: bundle_module_name, run_before, run_after

RegisterServicesHook
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: flask_unchained.hooks.register_services_hook.RegisterServicesHook
   :members:
   :inherited-members: bundle_override_module_name_attr
   :undoc-members: bundle_module_name, run_before, run_after

RunHooksHook
^^^^^^^^^^^^

.. automodule:: flask_unchained.hooks.run_hooks_hook
   :members: RunHooksHook
   :inherited-members: bundle_override_module_name_attr
   :undoc-members: bundle_module_name, run_before, run_after

FlaskForm
---------

.. automodule:: flask_unchained.forms.flask_form
   :members:

FlaskUnchained
--------------

.. automodule:: flask_unchained.flask_unchained
   :members:

Unchained
---------

.. automodule:: flask_unchained.unchained
   :members:
   :exclude-members: CategoryActionLog, ActionLogItem, ActionTableItem

Utilities
---------

Date Utilities
^^^^^^^^^^^^^^

.. automodule:: flask_unchained.utils
   :members: utcnow

Environment Variables
^^^^^^^^^^^^^^^^^^^^^

.. automodule:: flask_unchained.utils
   :members: get_boolean_env

String Utilities
^^^^^^^^^^^^^^^^

.. automodule:: flask_unchained.string_utils
   :members:

.. automodule:: flask_unchained.clips_pattern
   :members: pluralize, singularize

.. automodule:: flask_unchained.utils
   :members: format_docstring

Extension Development Utilities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: flask_unchained.utils
   :members: ConfigPropertyMeta, ConfigProperty

Metaclass Utilities
^^^^^^^^^^^^^^^^^^^

.. automodule:: flask_unchained.utils
   :members: deep_getattr

Subclassing Optional Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: flask_unchained.utils
   :members: OptionalMetaclass, OptionalClass

Attribute-access Dictionaries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: flask_unchained.utils.AttrDict
   :members:
