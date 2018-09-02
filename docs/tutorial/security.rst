Authentication and Authorization
--------------------------------

Flask Unchained currently has one officially supported bundle for securing your app. It's a heavily modified fork of the `Flask Security <https://pythonhosted.org/Flask-Security/>`_ project, and includes support for session and token authentication. Adding support for JWT and OAuth authentication are both on the roadmap, but are currently not yet implemented.

Install Flask Security Bundle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

   pip install flask-security-bundle

Let's update our test fixtures configuration file to include the test fixtures provided by Flask Security Bundle:

.. code:: python

   # tests/conftest.py

   from flask_unchained.bundles.sqlalchemy.pytest import *
   from flask_unchained.bundles.security.pytest import *  # add this line

The security bundle overrides the ``client`` and ``api_client`` test fixtures to add support for logging in and logging out. It also includes three fixtures specific to testing security views: ``registrations``, ``confirmations``, and ``password_resets``. We'll cover using these later on.

Now we can enable the bundle by updating ``unchained_config.py``:

.. code:: python

   # unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.security',
       'flaskr',
   ]

Database Models and Migrations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's start with configuring our database models, because the views will be broken until we implement our database models and create tables in the database for them. The security bundle includes default model implementations that, for now, will be sufficient for our needs:

.. code:: python

   # flask_unchained.bundles.security/models/user.py

   from flask_unchained.bundles.sqlalchemy import db
   from flask_unchained import unchained, injectable, lazy_gettext as _
   from flask_unchained.bundles.security.models.user_role import UserRole
   from flask_unchained.bundles.security.validators import EmailValidator

   MIN_PASSWORD_LENGTH = 8


   class User(db.Model):
       """
       Base :class:`User` model. Includes :attr:`email`, :attr:`password`, :attr:`active`,
       and :attr:`confirmed_at` columns, and a many-to-many relationship to the
       :class:`Role` model via the intermediary :class:`UserRole` join table.
       """
       class Meta:
           lazy_mapped = True

       email = db.Column(db.String(64), unique=True, index=True, info=dict(
           required=_('flask_unchained.bundles.security:email_required'),
           validators=[EmailValidator]))
       _password = db.Column('password', db.String, info=dict(
           required=_('flask_unchained.bundles.security:password_required')))
       active = db.Column(db.Boolean(name='active'), default=False)
       confirmed_at = db.Column(db.DateTime(), nullable=True)

       user_roles = db.relationship('UserRole', back_populates='user',
                                    cascade='all, delete-orphan')
       roles = db.association_proxy('user_roles', 'role',
                                    creator=lambda role: UserRole(role=role))

       __repr_props__ = ('id', 'email', 'active')

       @db.hybrid_property
       def password(self):
           return self._password

       @password.setter
       @unchained.inject('security_utils_service')
       def password(self, password, security_utils_service=injectable):
           self._password = security_utils_service.hash_password(password)

       @classmethod
       def validate_password(cls, password):
           if password and len(password) < MIN_PASSWORD_LENGTH:
               raise db.ValidationError(f'Password must be at least '
                                        f'{MIN_PASSWORD_LENGTH} characters long.')

       @unchained.inject('security_utils_service')
       def get_auth_token(self, security_utils_service=injectable):
           """
           Returns the user's authentication token.
           """
           return security_utils_service.get_auth_token(self)

       def has_role(self, role):
           """
           Returns `True` if the user identifies with the specified role.

           :param role: A role name or :class:`Role` instance
           """
           if isinstance(role, str):
               return role in (role.name for role in self.roles)
           else:
               return role in self.roles

       @property
       def is_authenticated(self):
           return True

       @property
       def is_anonymous(self):
           return False

.. code:: python

   # flask_unchained.bundles.security/models/role.py

   from flask_unchained.bundles.sqlalchemy import db
   from flask_unchained.bundles.security.models.user_role import UserRole

   class Role(db.Model):
       """
       Base :class`Role` model. Includes an :attr:`name` column and a many-to-many
       relationship with the :class:`User` model via the intermediary :class:`UserRole`
       join table.
       """
       class Meta:
           lazy_mapped = True

       name = db.Column(db.String(64), unique=True, index=True)

       role_users = db.relationship('UserRole', back_populates='role',
                                    cascade='all, delete-orphan')
       users = db.association_proxy('role_users', 'user',
                                    creator=lambda user: UserRole(user=user))

       __repr_props__ = ('id', 'name')

       def __hash__(self):
           return hash(self.name)

.. code:: python

   # flask_unchained.bundles.security/models/user_role.py

   from flask_unchained.bundles.sqlalchemy import db

   class UserRole(db.Model):
       """
       Join table between the :class:`User` and :class:`Role` models.
       """
       class Meta:
           lazy_mapped = True
           pk = None

       user_id = db.foreign_key('User', primary_key=True)
       user = db.relationship('User', back_populates='user_roles')

       role_id = db.foreign_key('Role', primary_key=True)
       role = db.relationship('Role', back_populates='role_users')

       __repr_props__ = ('user_id', 'role_id')

       def __init__(self, user=None, role=None, **kwargs):
           super().__init__(**kwargs)
           if user:
               self.user = user
           if role:
               self.role = role

We're going to leave them as-is for now, but in preparation for later customizations, let's subclass :class:`User` and :class:`Role` in our app bundle:

.. code:: bash

   touch app/models.py

.. code:: python

   # app/models.py

   from flask_unchained.bundles.security import User as BaseUser, Role as BaseRole, UserRole


   class User(BaseUser):
       pass


   class Role(BaseRole):
       pass

Time to generate some migrations:

.. code:: bash

   flask db migrate -m 'add security bundle models'

And review them to make sure it's going to do what we want:

.. code:: python

   # db/migrations/versions/[hash]_add_security_bundle_models.py

   """add security bundle models

   Revision ID: 839865db0b53
   Revises: eb0448e9a537
   Create Date: 2018-08-07 16:55:40.180962

   """
   from alembic import op
   import sqlalchemy as sa
   import flask_unchained.bundles.sqlalchemy.sqla.types as sqla_bundle

   # revision identifiers, used by Alembic.
   revision = '839865db0b53'
   down_revision = 'eb0448e9a537'
   branch_labels = None
   depends_on = None


   def upgrade():
       # ### commands auto generated by Alembic - please adjust! ###
       op.create_table('role',
           sa.Column('name', sa.String(length=64), nullable=False),
           sa.Column('id', sqla_bundle.BigInteger(), nullable=False),
           sa.Column('created_at', sqla_bundle.DateTime(timezone=True),
                     server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
           sa.Column('updated_at', sqla_bundle.DateTime(timezone=True),
                     server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
           sa.PrimaryKeyConstraint('id', name=op.f('pk_role'))
       )
       op.create_index(op.f('ix_role_name'), 'role', ['name'], unique=True)

       op.create_table('user',
           sa.Column('email', sa.String(length=64), nullable=False),
           sa.Column('password', sa.String(), nullable=False),
           sa.Column('active', sa.Boolean(name='active'), nullable=False),
           sa.Column('confirmed_at', sqla_bundle.DateTime(timezone=True), nullable=True),
           sa.Column('id', sqla_bundle.BigInteger(), nullable=False),
           sa.Column('created_at', sqla_bundle.DateTime(timezone=True),
                     server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
           sa.Column('updated_at', sqla_bundle.DateTime(timezone=True),
                     server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
           sa.PrimaryKeyConstraint('id', name=op.f('pk_user'))
       )
       op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)

       op.create_table('user_role',
           sa.Column('user_id', sqla_bundle.BigInteger(), nullable=False),
           sa.Column('role_id', sqla_bundle.BigInteger(), nullable=False),
           sa.Column('created_at', sqla_bundle.DateTime(timezone=True),
                     server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
           sa.Column('updated_at', sqla_bundle.DateTime(timezone=True),
                     server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
           sa.ForeignKeyConstraint(['role_id'], ['role.id'], name=op.f(
               'fk_user_role_role_id_role')),
           sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f(
               'fk_user_role_user_id_user')),
           sa.PrimaryKeyConstraint('user_id', 'role_id', name=op.f('pk_user_role'))
       )
       # ### end Alembic commands ###


   def downgrade():
       # ### commands auto generated by Alembic - please adjust! ###
       op.drop_table('user_role')
       op.drop_index(op.f('ix_user_email'), table_name='user')
       op.drop_table('user')
       op.drop_index(op.f('ix_role_name'), table_name='role')
       op.drop_table('role')
       # ### end Alembic commands ###

Looks good.

.. code:: bash

   flask db upgrade

Seeding the Database
^^^^^^^^^^^^^^^^^^^^

There is of course the manual method of creating users, either via the command line interface using ``flask users create``, or via the register endpoint (which we'll set up just after this). But the problem with those methods is that they're not reproducible. Database fixtures are one common solution to this problem, and the SQLAlchemy Bundle includes support for them.

First we need to create our fixtures directory and files. The file names must match the class name of the model each fixture corresponds to (``Role`` and ``User`` in our case):

.. code:: bash

   mkdir db/fixtures && touch db/fixtures/Role.yaml db/fixtures/User.yaml

.. code:: yaml

   # db/fixtures/Role.yaml

   ROLE_USER:
     name: ROLE_USER

   ROLE_ADMIN:
     name: ROLE_ADMIN

.. code:: yaml

   # db/fixtures/User.yaml

   admin:
     email: your_email@somewhere.com
     password: 'a secure password'
     active: True
     confirmed_at: utcnow
     roles: ['Role(ROLE_ADMIN, ROLE_USER)']

   user:
     email: user@flaskr.com
     password: password
     active: True
     confirmed_at: utcnow
     roles: ['Role(ROLE_USER)']

The keys in the yaml files, ``admin``, ``user``, ``ROLE_USER`` and ``ROLE_ADMIN``, must each be unique across all of your fixtures. This is because they are used to specify relationships. The syntax there is :python:`'ModelClassName(key1, Optional[key2, ...])'`. If the relationship is on the many side, as it is in our case, then the relationship specifier must also be surrounded by ``[]`` square brackets (yaml syntax to specify it's a list).

It's not shown above, but the fixture files are actually *Jinja2 templates that generate yaml*. Fixtures also have access to the excellent `faker <https://faker.readthedocs.io/en/master/>`_ library to generate random data, for example we could have written :code:`email: {{ faker.free_email() }}` in the ``user`` fixture. Between access to faker and the power of Jinja2, it's quite easy to build up a bunch of fake content when you need to quickly.

Running the fixtures should create two users and two roles in our dev db:

.. code:: bash

   flask db import-fixtures
   Loading fixtures from `db/fixtures` directory
   Created ROLE_USER: Role(id=1, name='ROLE_USER')
   Created ROLE_ADMIN: Role(id=2, name='ROLE_ADMIN')
   Created admin: User(id=1, email='your_email@somewhere.com', active=True)
   Created user: User(id=2, email='user@flaskr.com', active=True)
   Finished adding fixtures

Sweet. Let's set up our views so we can actually login to our site!

Configuring and Customizing Views
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first thing we need to do is to include the :class:`~flask_unchained.bundles.security.views.security_controller.SecurityController` in our ``routes.py``:

.. code:: python

   # app/routes.py

   from flask_unchained import (controller, resource, func, include, prefix,
                                get, post, patch, put, rule)

   from flask_unchained.bundles.security import SecurityController

   from .views import SiteController


   routes = lambda: [
       controller('/', SiteController),
       controller('/', SecurityController),
   ]

By default, Flask Security Bundle only comes with the login and logout endpoints enabled. Let's confirm:

.. code:: bash

   flask urls
   Method(s)  Rule                            Endpoint                                     View                                                                                           Options
   -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
         GET  /static/<path:filename>         static                                       flask.helpers :: send_static_file                                                              strict_slashes
         GET  /                               site_controller.index                        flaskr.views :: SiteController.index                                                           strict_slashes
         GET  /hello                          site_controller.hello                        flaskr.views :: SiteController.hello                                                           strict_slashes
   GET, POST  /login                          security_controller.login                    flask_unchained.bundles.security.views.security_controller :: SecurityController.login                    strict_slashes
         GET  /logout                         security_controller.logout                   flask_unchained.bundles.security.views.security_controller :: SecurityController.logout                   strict_slashes

The security bundle comes with optional support for registration, required email confirmation, change password functionality, and last but not least, forgot password functionality. For now, let's just enable registration:

.. code:: python

   # app/config.py

   class Config:
       # ...
       SECURITY_REGISTERABLE = True

Rerunning :code:`flask urls`, you should see the following line added:

.. code:: bash

   Method(s)  Rule                            Endpoint                                     View                                                                                           Options
   -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   GET, POST  /register                       security_controller.register                 flask_unchained.bundles.security.views.security_controller :: SecurityController.register                 strict_slashes

Let's add these routes to our navbar:

.. code:: html+jinja

   {# templates/_navbar.html #}

   <div class="collapse navbar-collapse" id="navbarCollapse">
     <ul class="navbar-nav mr-auto">
       {{ nav_link('Home', endpoint='site_controller.index') }}
       {{ nav_link('Hello', endpoint='site_controller.hello') }}
     </ul>
     <ul class="navbar-nav">
       {% if not current_user.is_authenticated %}
         {{ nav_link('Login', endpoint='security_controller.login') }}
         {{ nav_link('Register', endpoint='security_controller.register') }}
       {% else %}
         {{ nav_link('Logout', endpoint='security_controller.logout') }}
       {% endif %}
     </ul>
   </div>

Cool. You should now be able to login with the credentials you created in the ``User.yaml`` fixture. If you take a look at the login and/or register views, however, you'll notice that things aren't rendering "the bootstrap way." Luckily all the default templates in the security bundle extend the ``security/layout.html``, so we can override just this template to fix integrating the layout of all security views into our site.

We're going to completely override the layout template, but the relevant block looks like this (all of the security views render into ``block content``):

.. code:: html+jinja

   {% block body %}
     <div class="container">
       {% include '_flashes.html' %}
       {% block content %}
       {% endblock content %}
     </div>
   {% endblock body %}

So, in order to make sure the layout works correctly, we need to wrap the content block with a row and a column. Therefore, our version looks like this:

.. code:: bash

   mkdir -p app/templates/security \
      && touch app/templates/security/layout.html \
      && touch app/templates/security/_macros.html

.. code:: html+jinja

   {# app/templates/security/layout.html #}

   {% extends 'layout.html' %}

   {% block body %}
     <div class="container">
       {% include '_flashes.html' %}
       <div class="row">
         <div class="col">
           {% block content %}
           {% endblock content %}
         </div>
       </div>
     </div>
   {% endblock body %}

But even after this change, our forms are still using the browser's default form styling. Once again, the security bundle makes it easy to fix this, by overriding the ``render_form`` macro in the ``security/_macros.html`` template. You'll note we've already written this macro, so all we need to do is the following:

.. code:: html+jinja

   {# app/templates/security/_macros.html #}

   {% from '_macros.html' import render_form as _render_form %}

   {# the above is *only* an import, and Jinja doesn't re-export it, so we #}
   {# work around that by proxying to the original macro under the same name #}
   {% macro render_form(form) %}
     {{ _render_form(form, **kwargs) }}
   {% endmacro %}

Testing the Security Views
^^^^^^^^^^^^^^^^^^^^^^^^^^

Unlike all of our earlier tests, testing the security bundle views requires that we have valid users in the database. Perhaps the most powerful way to accomplish this is by using `Factory Boy <https://factoryboy.readthedocs.io/en/latest/>`_, which Flask Unchained comes integrated with out of the box. If you aren't familiar with Factory Boy, I recommend you read more about how it works in the official docs. The short version is, it makes it incredibly easy to dynamically create and customize models on-the-fly.

.. code:: python

   # tests/conftest.py

   import pytest

   from flask_unchained.bundles.sqlalchemy.pytest import *
   from flask_unchained.bundles.security.pytest import *

   from datetime import datetime, timezone
   from app.models import User, Role, UserRole


   class UserFactory(ModelFactory):
       class Meta:
           model = User

       email = 'user@example.com'
       password = 'password'
       active = True
       confirmed_at = datetime.now(timezone.utc)


   class RoleFactory(ModelFactory):
       class Meta:
           model = Role

       name = 'ROLE_USER'


   class UserRoleFactory(ModelFactory):
       class Meta:
           model = UserRole

       user = factory.SubFactory(UserFactory)
       role = factory.SubFactory(RoleFactory)


   class UserWithRoleFactory(UserFactory):
       user_role = factory.RelatedFactory(UserRoleFactory, 'user')


   @pytest.fixture()
   def user(request):
       kwargs = getattr(request.keywords.get('user'), 'kwargs', {})
       return UserWithRoleFactory(**kwargs)


   @pytest.fixture()
   def role(request):
       kwargs = getattr(request.keywords.get('role'), 'kwargs', {})
       return RoleFactory(**kwargs)

The :class:`ModelFactory` subclasses define the default values, and the ``user`` and ``role`` fixtures at the bottom make it possible to customize the values by marking the test, for example:

.. code:: python

   @pytest.mark.user(email='foo@bar.com')
   def test_something(user):
       assert user.email == 'foo@bar.com'

And our tests look like this:

.. code:: python

   # tests/security/test_security_controller.py

   from flask_unchained.bundles.security import AnonymousUser, current_user
   from flask_unchained import url_for


   class TestSecurityController:
       def test_login_get(self, client, templates):
           r = client.get('security_controller.login')
           assert r.status_code == 200
           assert templates[0].template.name == 'security/login.html'

       @pytest.mark.user(password='password')
       def test_login_post(self, client, user, templates):
           r = client.post('security_controller.login', data=dict(
               email=user.email,
               password='password'))

           assert r.status_code == 302
           assert r.path == url_for('site_controller.index')
           assert current_user == user

           r = client.follow_redirects(r)
           assert r.status_code == 200
           assert templates[0].template.name == 'site/index.html'

       def test_logout(self, client, user):
           client.login_user()
           assert current_user == user

           r = client.get('security_controller.logout')
           assert r.status_code == 302
           assert r.path == url_for('site_controller.index')
           assert isinstance(current_user._get_current_object(), AnonymousUser)

       def test_register_get(self, client, templates):
           r = client.get('security_controller.register')
           assert r.status_code == 200
           assert templates[0].template.name == 'security/register.html'

       def test_register_post_errors(self, client, templates):
           r = client.post('security_controller.register')
           assert r.status_code == 200
           assert templates[0].template.name == 'security/register.html'
           assert 'Email is required.' in r.html
           assert 'Password is required.' in r.html

       def test_register_post(self, client, registrations, user_manager):
           r = client.post('security_controller.register', data=dict(
               email='a@a.com',
               password='password',
               password_confirm='password'))
           assert r.status_code == 302
           assert r.path == url_for('site_controller.index')

           assert len(registrations) == 1
           user = user_manager.get_by(email='a@a.com')
           assert registrations[0]['user'] == user

Running them should pass:

.. code:: bash

   pytest --maxfail=1
   ================================== test session starts ===================================
   platform linux -- Python 3.6.6, pytest-3.7.1, py-1.5.4, pluggy-0.7.1
   rootdir: /home/user/dev/flaskr-unchained, inifile:
   plugins: flask-0.10.0, Flask-Unchained-0.5.1, Flask-Security-Bundle-0.3.0
   collected 11 items

   tests/app/test_views.py .....                                         [ 45%]
   tests/security/test_security_controller.py ......                                  [100%]

   =============================== 11 passed in 0.74 seconds ================================

You can learn more about how to use all of the features the security bundle supports in its documentation.

Let's commit our changes:

.. code:: bash

   git add .
   git status
   git commit -m 'install and configure security bundle'

 and move on to the meat of the application: :doc:`building_the_portfolio`.
