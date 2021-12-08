Adding an Admin Interface
-------------------------

Flask Unchained comes integrated with Flask-Admin. This is a secured section of the site which provides a GUI for staff to manage the data behind your site. As usual when adding a new bundle, we need to install it:

.. code:: shell

   pip install "flask-unchained[admin]"

And add the Admin Bundle to ``BUNDLES``:

.. code-block::

   # app/config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.admin',
       'app',
   ]

We also need to add its routes to our declarative routing tree:

.. code-block::

   # app/routes.py

   routes = lambda: [
       # ...
       include('flask_unchained.bundles.admin.routes'),
   ]

The Admin Bundle comes integrated with the Security Bundle by default, so you will need to use the admin user we added earlier to log into the site. You can also add a superuser from the command line like so:

.. code:: shell

   flask users create-superuser

Model Admins
^^^^^^^^^^^^

Once logged in, the default interface provides sections for managing users and roles (provided by the Security Bundle), but we need to add our own support for managing authors, quotes, and themes. Similar to model managers, you need a ``ModelAdmin`` subclass for each of the models you wish to manage through the admin interface.

AuthorAdmin
~~~~~~~~~~~

.. code-block::

   # app/admins/author_admin.py

   from flask_unchained.bundles.admin import ModelAdmin
   from flask_unchained.bundles.admin.templates import details_link, edit_link

   from ..models import Author


   class AuthorAdmin(ModelAdmin):
       model = Author

       # menu options
       category_name = 'Quotes'
       menu_icon_value = 'fa fa-user'

       # list view options
       column_list = ('id', 'name')
       column_default_sort = 'name'
       column_formatters = dict(
           name=edit_link('author'),
       )

       # edit view options
       create_modal = True
       edit_modal = True
       form_columns = ('name',)

       # details view options
       column_details_list = (
           'id',
           'name',
           'quotes',
           'created_at',
           'updated_at',
       )
       column_formatters_detail = dict(
           name=edit_link('author'),
           quotes=details_link('quote', label='quote', multiline_many=True),
       )

There's nothing too exciting going on here, we basically just have to tell Flask-Admin which model attributes we want to show up on the list, edit, and details views.

QuoteAdmin
~~~~~~~~~~

.. code-block::

   # app/admins/quote_admin.py

   from flask_unchained.bundles.admin import ModelAdmin
   from flask_unchained.bundles.admin.templates import edit_link

   from ..managers import ThemeManager
   from ..models import Quote


   class QuoteAdmin(ModelAdmin):
       model = Quote

       category_name = 'Quotes'
       menu_icon_value = 'fa fa-quote-left'

       column_filters = ('themes.name',)
       column_searchable_list = ('themes.name', 'author.name', 'quote')

       column_list = ('id', 'author', 'quote', 'themes')
       page_size = 100

       create_modal = True
       edit_modal = True
       form_columns = ('quote', 'author', 'themes')
       form_args = dict(
           themes=dict(query_factory=ThemeManager().all)
       )

       column_formatters = dict(
           quote=edit_link('quote'),
       )
       column_formatters_detail = dict(
           quote=edit_link('quote'),
       )
       column_details_list = (
           'id',
           'quote',
           'author',
           'themes',
           'created_at',
           'updated_at',
       )

ThemeAdmin
~~~~~~~~~~

.. code-block::

   # app/admins/theme_admin.py

   from flask_unchained.bundles.admin import ModelAdmin
   from flask_unchained.bundles.admin.templates import edit_link

   from ..models import Theme


   class ThemeAdmin(ModelAdmin):
       model = Theme

       category_name = 'Quotes'
       menu_icon_value = 'fa fa-lightbulb-o'

       column_list = ('id', 'name')
       column_default_sort = 'name'
       page_size = 100

       create_modal = True
       edit_modal = True
       form_columns = ('name', 'description', 'quotes')

       column_details_list = (
           'id',
           'name',
           'description',
           'quotes',
           'created_at',
           'updated_at',
       )

       column_formatters = dict(
           name=edit_link('theme'),
       )
       column_formatters_detail = dict(
           name=edit_link('theme'),
       )

Once the Admin Bundle is installed, and you've implemented model admins for each of your models, the admin interface is good to go. Let's add some links to our navbar to make it easier to get to:

.. code:: html+jinja

   {# templates/_navbar.html #}

   <nav class="navbar navbar-expand-md navbar-dark bg-dark">
     {# ... #}
     <div class="collapse navbar-collapse" id="navbarCollapse">
       <ul class="navbar-nav mr-auto">
         {{ nav_link('Home', endpoint='site_controller.index') }}
         {{ nav_link('Hello', endpoint='site_controller.hello') }}
         {{ nav_link('Authors', endpoint='site_controller.authors') }}
         {{ nav_link('Quotes', endpoint='site_controller.quotes') }}
         {{ nav_link('Themes', endpoint='site_controller.themes') }}
       </ul>
       <ul class="navbar-nav">
         {% if not current_user.is_authenticated %}
           {{ nav_link('Login', endpoint='security_controller.login') }}
           {{ nav_link('Register', endpoint='security_controller.register') }}
         {% else %}
           {% if current_user.is_admin %}
             {{ nav_link('Admin', endpoint='admin.index') }}
           {% endif %}
           {{ nav_link('Logout', endpoint='security_controller.logout') }}
         {% endif %}
       </ul>
     </div>
   </nav>

And that's all she wrote!
