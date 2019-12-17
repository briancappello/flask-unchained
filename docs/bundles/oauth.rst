OAuth Bundle
---------------

Integrates `Flask OAuthlib <http://flask-oauthlib.readthedocs.io/>`_ with Flask Unchained.
This allows OAuth authentication to any OAuth Provider supported by Flask OAuthlib.

Installation
^^^^^^^^^^^^

The OAuth Bundle depends on the Security Bundle, as well as a few third-party libraries:

.. code:: bash

   pip install "flask-unchained[oauth,security,sqlalchemy]"

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

    # your_app_bundle_root/routes.py

    from flask_unchained.bundles.oauth.views import OAuthController

    routes = lambda: [
        # ...
        controller(OAuthController),
    ]

Config
^^^^^^

The OAuth bundle includes support for two remote providers by default:

- amazon
- github

To configure these, would look like this:

.. code:: python

   # your_app_bundle_root/config.py

   import os

   from flask_unchained import BundleConfig

   class Config(BundleConfig):
       OAUTH_GITHUB_CONSUMER_KEY = os.getenv('OAUTH_GITHUB_CONSUMER_KEY', '')
       OAUTH_GITHUB_CONSUMER_SECRET = os.getenv('OAUTH_GITHUB_CONSUMER_SECRET', '')

       OAUTH_AMAZON_CONSUMER_KEY = os.getenv('OAUTH_AMAZON_CONSUMER_KEY', '')
       OAUTH_AMAZON_CONSUMER_SECRET = os.getenv('OAUTH_AMAZON_CONSUMER_SECRET', '')

You can also add other remote providers, for example to add support for the (made up) ``abc`` provider:

.. code:: python

   # your_app_bundle_root/config.py

   import os

   from flask_unchained import BundleConfig

   class Config(BundleConfig):
       OAUTH_REMOTE_APP_ABC = dict(
           consumer_key=os.getenv('OAUTH_ABC_CONSUMER_KEY', ''),
           consumer_secret=os.getenv('OAUTH_ABC_CONSUMER_SECRET', ''),
           base_url='https://api.abc.com/',
           access_token_url='https://abc.com/login/oauth/access_token',
           access_token_method='POST',
           authorize_url='https://abc.com/login/oauth/authorize'
           request_token_url=None,
           request_token_params={'scope': 'user:email'},
       )

Each remote provider is available at its respective endpoint: ``/login/<remote-app-name>``

For more information and OAuth config examples see:
    `Flask OAuthlib Examples <http://github.com/lepture/flask-oauthlib/tree/master/example>`_
