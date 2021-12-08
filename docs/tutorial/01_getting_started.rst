Getting Started
---------------

Install Flask Unchained
^^^^^^^^^^^^^^^^^^^^^^^

Create a new directory and enter it:

.. code:: bash

   mkdir hello-flask-unchained && cd hello-flask-unchained

The tutorial will assume you’re working from the ``hello-flask-unchained`` directory from now on. All commands are assumed to be run from this top-level project directory, and the file names at the top of each code block are also relative to this directory.

Next, let's create a new virtualenv, install Flask Unchained into it, and activate it:

.. code:: bash

   # create our virtualenv and activate it
   python3 -m venv venv && . venv/bin/activate

   # install flask-unchained
   pip install "flask-unchained[dev]"

   # reactivate the virtualenv so that pytest will work correctly
   deactivate && . venv/bin/activate

.. admonition:: Python Virtual Environments
    :class: note

    There are other ways to create virtualenvs for Python, and if you have a different preferred method that's fine, but you should always use a virtualenv by some way or another.

Project Layout
^^^^^^^^^^^^^^

Flask Unchained apps can be written either as a single file (a Python module) or in multiple files (a Python package) following a (configurable) naming convention. For now, let's keep it simple by using a single file named ``app.py``.

A Minimal Hello World App
^^^^^^^^^^^^^^^^^^^^^^^^^

The starting project layout of our Hello World app is two files:

.. code:: bash

   /home/user/dev/hello-flask-unchained
   ├── app.py
   └── test_app.py

Let's create them:

.. code:: bash

   touch app.py test_app.py

And the code:

.. code-block::

   # app.py

   from flask_unchained import AppBundle, Controller, route

   class App(AppBundle):
       pass

   class SiteController(Controller):
       @route('/')
       def index(self):
           return 'Hello Flask Unchained!'

Whenever you create a new app in Flask Unchained, you start by creating a new "app bundle": This is an overloaded term. The app bundle, conceptually, *is* your app. Literally, the app bundle is a subclass of :class:`~flask_unchained.AppBundle` that must live in your app bundle package's root (the ``app.py`` file here).

We can now start the development server with ``flask run`` and you should see your site running at `<http://localhost:5000>`_::

   flask run
    * Environment: development
    * Debug mode: on
    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

Let's add a quick test before we continue.

.. code:: python

   # test_app.py

   class TestSiteController:
       def test_index(self, client):
           r = client.get('site_controller.index')
           assert r.status_code == 200
           assert r.html.count('Hello Flask Unchained!') == 1

Here, we're using the HTTP ``client`` pytest fixture to request the URL for the endpoint ``"site_controller.index"``, verifying the response has a status code of ``200``, and lastly checking that the string ``"Hello Flask Unchained!"`` is in the response.

Let's make sure it passes:

.. code:: bash

   pytest
   ======================== test session starts ========================
   platform linux -- Python 3.6.6, pytest-3.6.4, py-1.5.4, pluggy-0.7.1
   rootdir: /home/user/dev/hello-flask-unchained, inifile:
   plugins: flask-0.10.0, Flask-Unchained-0.8.0
   collected 1 item

   test_app.py .                                                   [100%]
   ======================== 1 passed in 0.18 seconds ====================

NOTE: If you get any errors, you may need to deactivate and reactivate your virtualenv if you haven't already since installing ``pytest``.

If you haven't already, now would be a good time to initialize a git repo and make our first commit. Before we do that though, let's add a ``.gitignore`` file to make sure we don't commit anything that shouldn't be.

.. code:: bash

   # .gitignore

   *.egg-info
   *.pyc
   .coverage
   .cache/
   .pytest_cache/
   .tox/
   __pycache__/
   build/
   coverage_html_report/
   db/*.sqlite
   dist/
   docs/_build
   venv/

Initialize the repo and make our first commit:

.. code:: bash

   git init
   git add .

   # review to make sure it's not going to do anything you don't want it to:
   git status

   git commit -m 'initial hello world commit'

OK, everything works, but this is about as basic as it gets. Let's make things a bit more interesting by moving on to :doc:`02_views_templates_and_static_assets`.
