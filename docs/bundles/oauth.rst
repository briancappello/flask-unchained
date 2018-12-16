OAuth Bundle
---------------

Integrates `Flask OAuthlib <http://flask-oauthlib.readthedocs.io/>`_ with Flask Unchained.
This allows OAuth authentication to any OAuth Provider supported by Flask OAuthlib.

Installation
^^^^^^^^^^^^

The OAuth Bundle depends on the Security Bundle, as well as a few third-party libraries:

.. code:: bash

   pip install flask-unchained[oauth,security,sqlalchemy]

And enable the bundles in your ``unchained_config.py``:

.. code:: python

   # your_project_root/unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.sqlalchemy',
       'flask_unchained.bundles.security',
       'flask_unchained.bundles.oauth',
       'app',
   ]

And set the OAuthController to your app's ``routes.py``:

.. code:: python

    # your_app_root/routes.py

    from flask_unchained.bundles.oauth.views import OAuthController

    routes = lambda: [
        controller(SiteController),
        controller(OAuthController),
    ]

Config
^^^^^^

.. code:: python

    # your_app_root/config.py

    class ProdConfig(Config):
        OAUTH_REMOTE_APP_GITHUB = dict(
            consumer_key='',
            consumer_secret='',
            request_token_params={'scope': 'user:email'},
            base_url='https://api.github.com/',
            request_token_url=None,
            access_token_method='POST',
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize'
        )

This configuration will be available at the endpoint '/login/github'.

A second configuration for gitlab as oauth provider could be called OAUTH_REMOTE_APP_GITLAB = dict(...)
which will be available at the endpoint 'login/gitlab'.

For more information and oauth config examples see:
    `Flask OAuthlib Examples <http://github.com/lepture/flask-oauthlib/tree/master/example>`_
