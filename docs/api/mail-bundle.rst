Mail Bundle API
---------------

**flask_unchained.bundles.mail**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.mail.MailBundle

**flask_unchained.bundles.mail.config**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.mail.config.Config
    ~flask_unchained.bundles.mail.config.DevConfig
    ~flask_unchained.bundles.mail.config.ProdConfig
    ~flask_unchained.bundles.mail.config.StagingConfig
    ~flask_unchained.bundles.mail.config.TestConfig

**flask_unchained.bundles.mail.extensions**

.. autosummary::
    :nosignatures:

    ~flask_unchained.bundles.mail.Mail

MailBundle
^^^^^^^^^^
.. autoclass:: flask_unchained.bundles.mail.MailBundle
    :members:

Config
^^^^^^
.. automodule:: flask_unchained.bundles.mail.config
    :members: Config, DevConfig, ProdConfig, StagingConfig, TestConfig

The Mail Extension
^^^^^^^^^^^^^^^^^^
.. autoclass:: flask_unchained.bundles.mail.Mail
    :members: send_message
