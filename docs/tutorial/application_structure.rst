Application Structure
---------------------

Our app currently consists of only a single file. This works, and you could continue adding things to it if you wanted to. That said, Flask Unchained is primarily designed for building much larger apps, and that's where your sanity will benefit greatly if things are more organized.

Let's start by refactoring our current code. We need a new directory structure to work with::

   /home/user/dev/hello-flask-unchained
   ├── unchained_config.py
   ├── app
   │   ├── __init__.py
   │   ├── templates
   │   │   └── site
   │   │       └── index.html
   │   └── views.py
   └── tests
       ├── __init__.py
       └── app
           └── test_views.py

.. code:: bash

   mkdir -p app app/templates/site tests/app \
     && mv app.py app/__init__.py && touch unchained_config.py \
     && touch app/views.py app/templates/site/index.html \
     && mv test_app.py tests/app/test_views.py

There are some minor code changes we need to make now:

.. code:: python

   # app/__init__.py

   from flask_unchained import AppBundle

   class App(AppBundle):
       pass

.. code:: python

   # unchained_config.py

   BUNDLES = [
       'app',  # your app bundle *must* be last
   ]

This code specifies that the `app` Python package (module) is our app bundle. Previously, when we were using a single file for the app bundle, this ``BUNDLES`` declaration is (optionally) implicit. However, when the app bundle is a multi-file Python package, then we need to be explicit in telling Flask Unchained which bundles to load.

.. code:: python

   # app/views.py

   from flask_unchained import Controller, route

   class SiteController(Controller):
       @route('/')
       def index(self):
           return self.render('site/index.html')  # template name in longhand
           # return self.render('index')  # or the same, in shorthand

Here, instead of returning a string, we're rendering the following template:

.. code:: html+jinja

   {# app/templates/site/index.html #}

   <html>
     <head>
       <title>Hello World!</title>
     </head>
     <body>
       <h1>Hello World!</h1>
     </body>
   </html>

And lastly, because we added the ``title`` tag to the template, we also need to update our tests to expect 2 occurrences of the string ``"Hello World!"``:

.. code:: python

   # tests/app/test_views.py

   class TestSiteController:
       def test_index(self, client):
           r = client.get('site_controller.index')
           assert r.status_code == 200
           assert r.html.count('Hello World!') == 2

In the first iteration of our hello world app, we didn't have an explicit ``unchained_config`` module in our project root, and as such we had to specify the ``UNCHAINED_CONFIG`` environment variable when running our app. This time, it will be found automatically:

.. code:: bash

   flask run
    * Environment: development
    * Debug mode: on
    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

Same for running the tests:

.. code:: bash

   pytest
   ======================== test session starts ========================
   platform linux -- Python 3.6.6, pytest-3.6.4, py-1.5.4, pluggy-0.7.1
   rootdir: /home/user/dev/hello-flask-unchained, inifile:
   plugins: flask-0.10.0, Flask-Unchained-0.8.0
   collected 1 item

   tests/app/test_views.py .                                       [100%]
   ======================== 1 passed in 0.18 seconds ====================

Sweet. Let's make another commit:

.. code:: bash

   git add .
   git status
   git commit -m 'refactor app bundle into a package'

And next let's move on to :doc:`templates_and_static_assets`.
