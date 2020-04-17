Security Bundle API
-------------------

**flask_unchained.bundles.security**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.security.SecurityBundle

**flask_unchained.bundles.security.config**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.security.config.Config
    ~flask_unchained.bundles.security.config.AuthenticationConfig
    ~flask_unchained.bundles.security.config.TokenConfig
    ~flask_unchained.bundles.security.config.RegistrationConfig
    ~flask_unchained.bundles.security.config.ChangePasswordConfig
    ~flask_unchained.bundles.security.config.ForgotPasswordConfig
    ~flask_unchained.bundles.security.config.EncryptionConfig

**flask_unchained.bundles.security.extensions**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.security.Security

**flask_unchained.bundles.security.views**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.security.SecurityController
    ~flask_unchained.bundles.security.UserResource

**flask_unchained.bundles.security.decorators**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.security.auth_required
    ~flask_unchained.bundles.security.auth_required_same_user
    ~flask_unchained.bundles.security.anonymous_user_required

**flask_unchained.bundles.security.models**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.security.User
    ~flask_unchained.bundles.security.Role
    ~flask_unchained.bundles.security.UserRole

**flask_unchained.bundles.security.serializers**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.security.serializers.UserSerializer
    ~flask_unchained.bundles.security.serializers.RoleSerializer

**flask_unchained.bundles.security.services**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.security.SecurityService
    ~flask_unchained.bundles.security.SecurityUtilsService
    ~flask_unchained.bundles.security.UserManager
    ~flask_unchained.bundles.security.RoleManager

**flask_unchained.bundles.security.forms**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.security.forms.LoginForm
    ~flask_unchained.bundles.security.forms.RegisterForm
    ~flask_unchained.bundles.security.forms.ChangePasswordForm
    ~flask_unchained.bundles.security.forms.ForgotPasswordForm
    ~flask_unchained.bundles.security.forms.ResetPasswordForm
    ~flask_unchained.bundles.security.forms.SendConfirmationForm

SecurityBundle
^^^^^^^^^^^^^^
.. autoclass:: flask_unchained.bundles.security.SecurityBundle
   :members:

Config
^^^^^^

.. autosummary::
    ~flask_unchained.bundles.security.config.Config
    ~flask_unchained.bundles.security.config.AuthenticationConfig
    ~flask_unchained.bundles.security.config.TokenConfig
    ~flask_unchained.bundles.security.config.RegistrationConfig
    ~flask_unchained.bundles.security.config.ChangePasswordConfig
    ~flask_unchained.bundles.security.config.ForgotPasswordConfig
    ~flask_unchained.bundles.security.config.EncryptionConfig

General
~~~~~~~
.. autoclass:: flask_unchained.bundles.security.config.Config
   :members:

Authentication
~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.config.AuthenticationConfig
   :members:

Token Authentication
~~~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.config.TokenConfig
   :members:

Registration
~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.config.RegistrationConfig
   :members:

Change Password
~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.config.ChangePasswordConfig
   :members:

Forgot Password
~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.config.ForgotPasswordConfig
   :members:

Encryption
~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.config.EncryptionConfig
   :members:

The Security Extension
^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: flask_unchained.bundles.security.Security
   :members:

Views
^^^^^

Decorators
~~~~~~~~~~
.. autofunction:: flask_unchained.bundles.security.auth_required
.. autofunction:: flask_unchained.bundles.security.auth_required_same_user
.. autofunction:: flask_unchained.bundles.security.anonymous_user_required

SecurityController
~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.SecurityController
   :members:

UserResource
~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.UserResource
   :members:

Models and Managers
^^^^^^^^^^^^^^^^^^^

User
~~~~
.. autoclass:: flask_unchained.bundles.security.User
   :members:

UserManager
~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.UserManager
   :members:

Role
~~~~
.. autoclass:: flask_unchained.bundles.security.Role
   :members:

RoleManager
~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.RoleManager
   :members:

UserRole
~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.UserRole
   :members:

Serializers
^^^^^^^^^^^

UserSerializer
~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.serializers.UserSerializer
   :members:

RoleSerializer
~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.serializers.RoleSerializer
   :members:

Services
^^^^^^^^

SecurityService
~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.SecurityService
   :members:

SecurityUtilsService
~~~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.SecurityUtilsService
   :members:

Forms
^^^^^

LoginForm
~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.forms.LoginForm
   :members:

RegisterForm
~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.forms.RegisterForm
   :members:

ChangePasswordForm
~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.forms.ChangePasswordForm
   :members:

ForgotPasswordForm
~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.forms.ForgotPasswordForm
   :members:

ResetPasswordForm
~~~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.forms.ResetPasswordForm
   :members:

SendConfirmationForm
~~~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_unchained.bundles.security.forms.SendConfirmationForm
   :members:

Validators
~~~~~~~~~~
.. autofunction:: flask_unchained.bundles.security.forms.password_equal
.. autofunction:: flask_unchained.bundles.security.forms.new_password_equal
.. autofunction:: flask_unchained.bundles.security.forms.unique_user_email
.. autofunction:: flask_unchained.bundles.security.forms.valid_user_email
