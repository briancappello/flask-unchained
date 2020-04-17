SQLAlchemy Bundle API
---------------------

**flask_unchained.bundles.sqlalchemy**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.sqlalchemy.SQLAlchemyBundle

**flask_unchained.bundles.sqlalchemy.config**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.sqlalchemy.config.Config
    ~flask_unchained.bundles.sqlalchemy.config.TestConfig

**flask_unchained.bundles.sqlalchemy.extensions**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.sqlalchemy.SQLAlchemyUnchained

**flask_unchained.bundles.sqlalchemy.hooks**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.sqlalchemy.hooks.RegisterModelsHook

**flask_unchained.bundles.sqlalchemy.services**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.sqlalchemy.SessionManager
    ~flask_unchained.bundles.sqlalchemy.ModelManager

**flask_unchained.bundles.sqlalchemy.sqla**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.sqlalchemy.sqla.Column
    ~flask_unchained.bundles.sqlalchemy.sqla.attach_events
    ~flask_unchained.bundles.sqlalchemy.sqla.on
    ~flask_unchained.bundles.sqlalchemy.sqla.slugify
    ~flask_unchained.bundles.sqlalchemy.sqla.foreign_key

**flask_unchained.bundles.sqlalchemy.forms**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.sqlalchemy.forms.ModelForm

SQLAlchemyBundle
^^^^^^^^^^^^^^^^
.. autoclass:: flask_unchained.bundles.sqlalchemy.SQLAlchemyBundle
   :members:

Config
^^^^^^
.. automodule:: flask_unchained.bundles.sqlalchemy.config
   :members:

The SQLAlchemy Extension
^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: flask_unchained.bundles.sqlalchemy.SQLAlchemyUnchained
   :members:

RegisterModelsHook
^^^^^^^^^^^^^^^^^^
.. autoclass:: flask_unchained.bundles.sqlalchemy.hooks.RegisterModelsHook
    :members:

Services
^^^^^^^^
.. autoclass:: flask_unchained.bundles.sqlalchemy.SessionManager
   :members:

.. autoclass:: flask_unchained.bundles.sqlalchemy.ModelManager
   :members:

ModelForm
^^^^^^^^^^
.. autoclass:: flask_unchained.bundles.sqlalchemy.forms.ModelForm
   :members:

SQLAlchemy
^^^^^^^^^^

Column
~~~~~~
.. autoclass:: flask_unchained.bundles.sqlalchemy.sqla.Column
    :members:

foreign_key
~~~~~~~~~~~
.. autofunction:: flask_unchained.bundles.sqlalchemy.sqla.foreign_key

events
~~~~~~
.. autofunction:: flask_unchained.bundles.sqlalchemy.sqla.on
.. autofunction:: flask_unchained.bundles.sqlalchemy.sqla.attach_events
.. autofunction:: flask_unchained.bundles.sqlalchemy.sqla.slugify
