Security Bundle
---------------

.. autoclass:: flask_unchained.bundles.security.SecurityBundle
   :members:


Config
^^^^^^

.. automodule:: flask_unchained.bundles.security.config
   :members:

Security Extension
^^^^^^^^^^^^^^^^^^

.. autoclass:: flask_unchained.bundles.security.extensions.security.Security
   :members:

Decorators
^^^^^^^^^^

.. autofunction:: flask_unchained.bundles.security.auth_required

.. autofunction:: flask_unchained.bundles.security.auth_required_same_user

.. autofunction:: flask_unchained.bundles.security.anonymous_user_required

Forms
^^^^^

LoginForm
"""""""""

.. autoclass:: flask_unchained.bundles.security.forms.LoginForm
   :members:

ForgotPasswordForm
""""""""""""""""""

.. autoclass:: flask_unchained.bundles.security.forms.ForgotPasswordForm
   :members:

ChangePasswordForm
""""""""""""""""""

.. autoclass:: flask_unchained.bundles.security.forms.ChangePasswordForm
   :members:

RegisterForm
""""""""""""

.. autoclass:: flask_unchained.bundles.security.forms.RegisterForm
   :members:

ResetPasswordForm
"""""""""""""""""

.. autoclass:: flask_unchained.bundles.security.forms.ResetPasswordForm
   :members:

SendConfirmationForm
""""""""""""""""""""

.. autoclass:: flask_unchained.bundles.security.forms.SendConfirmationForm
   :members:

Validators
""""""""""

.. autofunction:: flask_unchained.bundles.security.forms.password_equal
.. autofunction:: flask_unchained.bundles.security.forms.new_password_equal
.. autofunction:: flask_unchained.bundles.security.forms.unique_user_email
.. autofunction:: flask_unchained.bundles.security.forms.valid_user_email

Models
^^^^^^

User
""""

.. autoclass:: flask_unchained.bundles.security.User
   :members:

Role
""""

.. autoclass:: flask_unchained.bundles.security.Role
   :members:

UserRole
""""""""

.. autoclass:: flask_unchained.bundles.security.UserRole
   :members:

Serializers
^^^^^^^^^^^

UserSerializer
""""""""""""""

.. autoclass:: flask_unchained.bundles.security.serializers.UserSerializer
   :members:

RoleSerializer
""""""""""""""

.. autoclass:: flask_unchained.bundles.security.serializers.RoleSerializer
   :members:

Services
^^^^^^^^

SecurityService
"""""""""""""""

.. autoclass:: flask_unchained.bundles.security.SecurityService
   :members:

SecurityUtilsService
""""""""""""""""""""

.. autoclass:: flask_unchained.bundles.security.SecurityUtilsService
   :members:

UserManager
"""""""""""

.. autoclass:: flask_unchained.bundles.security.UserManager
   :members:

RoleManager
"""""""""""

.. autoclass:: flask_unchained.bundles.security.RoleManager
   :members:

Views
^^^^^

SecurityController
""""""""""""""""""

.. autoclass:: flask_unchained.bundles.security.SecurityController
   :members:

UserResource
""""""""""""

.. autoclass:: flask_unchained.bundles.security.UserResource
   :members:
