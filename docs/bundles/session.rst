Session Bundle
--------------

Integrates `Flask Session <https://pythonhosted.org/Flask-Session/>`_ with Flask Unchained. This bundle is only a thin wrapper around Flask Session, and usage in Flask Unchained is as simple as it gets. Enable the bundle, configure ``SESSION_TYPE``, and you're off running.

Installation
^^^^^^^^^^^^

Install dependencies:

.. code:: bash

   pip install "flask-unchained[session]"

And enable the bundle in your ``unchained_config.py``:

.. code:: python

   # your_project_root/unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.session',
       'app',
   ]

Config
^^^^^^

You must configure ``SESSION_TYPE``, and depending upon what you set it to, any other required options for that type:

================  ================================================================================
SESSION_TYPE      Extra Required Options
================  ================================================================================
``'null'``        (none)
``'redis'``       * :attr:`~flask_unchained.bundles.session.config.Config.SESSION_REDIS`
``'memcached'``   * :attr:`~flask_unchained.bundles.session.config.Config.SESSION_MEMCACHED`
``'filesystem'``  * :attr:`~flask_unchained.bundles.session.config.Config.SESSION_FILE_DIR`
                  * :attr:`~flask_unchained.bundles.session.config.Config.SESSION_FILE_THRESHOLD`
                  * :attr:`~flask_unchained.bundles.session.config.Config.SESSION_FILE_MODE`
``'mongodb'``     * :attr:`~flask_unchained.bundles.session.config.Config.SESSION_MONGODB`
                  * :attr:`~flask_unchained.bundles.session.config.Config.SESSION_MONGODB_DB`
                  * :attr:`~flask_unchained.bundles.session.config.Config.SESSION_MONGODB_COLLECT`
``'sqlalchemy'``  * :attr:`~flask_unchained.bundles.session.config.Config.SESSION_SQLALCHEMY`
                  * :attr:`~flask_unchained.bundles.session.config.Config.SESSION_SQLALCHEMY_TABLE`
                  * :attr:`~flask_unchained.bundles.session.config.Config.SESSION_SQLALCHEMY_MODEL`
================  ================================================================================

.. automodule:: flask_unchained.bundles.session.config
   :members:
   :noindex:

API Docs
^^^^^^^^

See :doc:`../api/session-bundle`
