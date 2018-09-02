Security Bundle
---------------

Integrates `Flask Login <http://flask-login.readthedocs.io/>`_ and `Flask Principal <https://pythonhosted.org/Flask-Principal/>`_ with Flask Unchained. Technically speaking, this bundle is actually a heavily refactored fork of the `Flask Security <https://pythonhosted.org/Flask-Security/>`_ project. As of this writing, it is at approximate feature parity with Flask Security, and supports session and token authentication. (We've removed support for HTTP Basic Auth, tracking users' IP addresses and similar, as well as the experimental password-less login support.)

Installation
^^^^^^^^^^^^

The Security Bundle depends on the SQLAlchemy Bundle, as well as a few third-party libraries:

.. code:: bash

   pip install flask-unchained[security,sqlalchemy]

And enable the bundles in your ``unchained_config.py``:

.. code:: python

   # your_project_root/unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.sqlalchemy',
       'flask_unchained.bundles.security',
   ]

Config
^^^^^^

.. automodule:: flask_unchained.bundles.security.config
   :members:
   :noindex:

Commands
^^^^^^^^

.. click:: flask_unchained.bundles.security.commands.users:users
   :prog: flask users
   :show-nested:

.. click:: flask_unchained.bundles.security.commands.roles:roles
   :prog: flask roles
   :show-nested:

API Documentation
^^^^^^^^^^^^^^^^^

:doc:`../api/bundles/security`
