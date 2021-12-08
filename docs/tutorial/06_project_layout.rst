Project Layout
--------------

So far we've been building our app as a single file. This is fine for smaller apps but as our apps grow bigger it's best to split things out into multiple files. To review, our app currently looks like this:

.. code-block::

   # app.py

   from flask_unchained import AppBundle, BundleConfig, Controller, route, param_converter
   from flask_unchained.forms import FlaskForm, fields, validators
   from flask_unchained import (controller, resource, func, include, prefix,
                                get, delete, post, patch, put, rule)
   from flask_unchained.bundles.security import SecurityController
   from flask_unchained.bundles.security.models import User as BaseUser, Role as BaseRole

   BUNDLES = [
       'flask_unchained.bundles.sqlalchemy',
       'flask_unchained.bundles.session',
       'flask_unchained.bundles.security',
       'py_yaml_fixtures',
   ]


   class Config(BundleConfig):
       SECRET_KEY = 'super-sekret'
       WTF_CSRF_ENABLED = True
       SESSION_TYPE = 'sqlalchemy'
       SECURITY_REGISTERABLE = True


   class TestConfig(Config):
       WTF_CSRF_ENABLED = False


   class App(AppBundle):
       pass


   class User(BaseUser):
       pass


   class Role(BaseRole):
       pass


   class HelloForm(FlaskForm):
       name = fields.StringField('Name', validators=[
           validators.DataRequired('Name is required.')])
       submit = fields.SubmitField('Submit')


   class SiteController(Controller):
       @route('/')
       def index(self):
           return self.render('index')

       @route(methods=['GET', 'POST'])
       @param_converter(name=str)
       def hello(self, name=None):
           form = HelloForm()
           if form.validate_on_submit():
               return self.redirect('hello', name=form.name.data)
           return self.render('hello', hello_form=form, name=name or 'World')


   routes = lambda: [
       controller(SiteController),
       controller(SecurityController),
   ]

The file structure we're going to refactor to looks like this:

.. code:: shell

   /home/user/dev/hello-flask-unchained
   ├── app/
   │   ├── __init__.py
   │   ├── config.py
   │   ├── routes.py
   │   ├── models/
   │   │   ├── __init__.py
   │   │   └── user.py
   │   ├── templates/
   │   │   ├── security/
   │   │   │   ├── layout.html
   │   │   │   └── _macros.html
   │   │   └── site/
   │   │       ├── hello.html
   │   │       └── index.html
   │   └── views/
   │       ├── __init__.py
   │       ├── forms.py
   │       └── site_controller.py
   ├── db/
   │   ├── development.sqlite
   │   ├── fixtures.yaml
   │   └── migrations/
   ├── static/
   │   ├── main.css
   │   └── vendor/
   ├── templates/
   │   ├── layout.html
   │   ├── _flashes.html
   │   ├── _macros.html
   │   └── _navbar.html
   └── tests/
       ├── __init__.py
       ├── conftest.py
       └── app/
           └── views/
               ├── test_security_controller.py
               └── test_site_controller.py

All of these module names are the defaults; you don't have to configure anything special for your app to continue working after splitting out the code. Just as when using a single file, everything starts with the ``AppBundle``:

.. code-block::

   # app/__init__.py

   from flask_unchained import AppBundle


   class App(AppBundle):
       pass

There is *one* minor difference to note when using a package for the app bundle, and that is that you must list the app bundle's module name in ``BUNDLES``:

.. code-block::

   # app/config.py

   from flask_unchained import BundleConfig


   BUNDLES = [
       'flask_unchained.bundles.sqlalchemy',
       'flask_unchained.bundles.session',
       'flask_unchained.bundles.security',
       'py_yaml_fixtures',
       'app',  # your app bundle *must* be last
   ]


   class Config(BundleConfig):
       SECRET_KEY = 'super-sekret'
       WTF_CSRF_ENABLED = True
       SESSION_TYPE = 'sqlalchemy'
       SECURITY_REGISTERABLE = True


   class TestConfig(Config):
       WTF_CSRF_ENABLED = False

The rest of the code is just copy-paste (with a few additional/modified imports):

.. code-block::

   # app/models/__init__.py

   from flask_unchained.bundles.security import Role, UserRole

   from .user import User

.. code-block::

   # app/models/user.py

   from flask_unchained.bundles.security import User as BaseUser


   class User(BaseUser):
       pass

.. code-block::

   # app/views/__init__.py

   from flask_unchained.bundles.security import SecurityController

   from .site_controller import SiteController

.. code-block::

   # app/views/forms.py

   from flask_unchained.forms import FlaskForm, fields, validators


   class HelloForm(FlaskForm):
       name = fields.StringField('Name', validators=[
           validators.DataRequired('Name is required.')])
       submit = fields.SubmitField('Submit')

.. code-block::

   # app/views/site_controller.py

   from flask_unchained import Controller, route, param_converter

   from .forms import HelloForm


   class SiteController(Controller):
       @route('/')
       def index(self):
           return self.render('index')

       @route(methods=['GET', 'POST'])
       @param_converter(name=str)
       def hello(self, name=None):
           form = HelloForm()
           if form.validate_on_submit():
               return self.redirect('hello', name=form.name.data)
           return self.render('hello', hello_form=form, name=name or 'World')

.. code-block::

   # app/routes.py

   from flask_unchained import (controller, resource, func, include, prefix,
                                get, delete, post, patch, put, rule)

   from . import views

   routes = lambda: [
       controller(views.SiteController),
       controller(views.SecurityController),
   ]

For the template files and tests, they will continue to work in their top-level folders, however, it's best to organize them into the bundle:

.. code:: bash

   mv templates/security app/templates/security && \
      mv templates/site app/templates/site

   mkdir -p tests/app/views && \
      mv tests/test_* tests/app/views/

.. admonition:: Customizing Your Bundle Layout
   :class: info

   If you want to change the module names of where things live, you can do so like this:

   .. code-block::

      # app/__init__.py

      from flask_unchained import AppBundle

      class App(AppBundle):
          command_group_names = ['app']                               # default is bundle.name
          config_module_name = 'settings'                             # default is 'config'
          routes_module_name = 'urls'                                 # default is 'routes'
          models_module_names = ['models']                            # the default
          services_module_names = ['services', 'managers']            # the default
          template_folder = 'templates'                               # the default
          views_module_names = ['controllers', 'resources', 'views']  # default is ['views']

   The attribute names to set on your ``Bundle`` subclass can be discovered by running ``flask unchained hooks`` at the command prompt.

   While this is supported, it is recommended to leave things at their defaults so that other developers can more easily find their way around your code.

Tests should still pass, so it's time to make a commit:

.. code:: bash

   git add .
   git status
   git commit -m 'refactor app bundle into a package'

Now that we've covered the basics, let's move on to building out the main functionality of our application: :doc:`07_modeling_authors_quotes_themes`.
