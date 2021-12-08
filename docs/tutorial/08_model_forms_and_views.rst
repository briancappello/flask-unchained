Model Forms and Views
---------------------

In this section we'll build out the frontend for our site. Our users should be able to browse the authors, quotes and themes in the database, as well as add their own. Let's start with the form classes.

Model Forms
^^^^^^^^^^^

A ``ModelForm`` is a "smart" form that can determine its fields from the model class you give it. It's not perfect, as we'll see below - you do need to help it out some, especially when it comes to relationships.

.. code-block::

   # views/forms.py

   from flask_unchained.forms import FlaskForm, fields, validators
   from flask_unchained.bundles.sqlalchemy.forms import ModelForm, QuerySelectMultipleField

   from .. import models, managers


   class AuthorForm(ModelForm):
       class Meta:
           model = models.Author
           only = ('name',)


   class QuoteForm(ModelForm):
       class Meta:
           model = models.Quote
           only = ('author', 'quote', 'themes')
           field_args = {
               'author': dict(allow_blank=True,
                              blank_text='Select...',
                              query_factory=managers.AuthorManager().all),
           }

       themes = QuerySelectMultipleField(
           query_factory=managers.ThemeManager().all,
       )
       field_order = ('author', 'quote', 'themes')


   class ThemeForm(ModelForm):
       class Meta:
           model = models.Theme
           only = ('name', 'description')

All model forms require ``Meta.model`` to be specified. We use ``Meta.only`` to limit the fields the form will show - users should not be able to modify the ``created_at`` or ``updated_at`` timestamps, for example. You can see this in action with the simplest two forms, ``AuthorForm`` and ``ThemeForm``.

When it comes to relationships, we need to provide some help. Starting with ``QuoteForm``, ``ModelForm`` is smart enough to guess the correct type of field for author, and we use ``Meta.field_args`` to customize the arguments passed to it. However, with many-to-many relationships, because we're actually leveraging association proxies on the model underneath, we need to define the fields ourself. You can see this with ``QuoteForm.themes``.

Views
^^^^^

We'll add five new views: one each for listing quotes, authors, and themes, as well as detail views for individual authors and themes. We use dependency injection on our controller to gain access to the model manager instances so that we can query the database for models and save them upon form submission.

.. code-block::

   # app/views/site_controller.py

   from flask_unchained import Controller, route, param_converter, injectable

   from . import forms
   from .. import models, managers


   class SiteController(Controller):
       author_manager: managers.AuthorManager = injectable
       quote_manager: managers.QuoteManager = injectable
       quote_list_manager: managers.QuoteListManager = injectable
       theme_manager: managers.ThemeManager = injectable

       # ...

       @route(methods=['GET', 'POST'])
       def quotes(self):
           form = forms.QuoteForm()
           if form.validate_on_submit():
               quote = form.make_instance()
               self.quote_manager.save(quote, commit=True)
               self.flash('New quote added!', category='success')
               return self.redirect('quotes')

           return self.render('quotes', quotes=self.quote_manager.all(), form=form)

       @route(methods=['GET', 'POST'])
       def authors(self):
           form = forms.AuthorForm()
           if form.validate_on_submit():
               author = form.make_instance()
               self.author_manager.save(author, commit=True)
               self.flash('New author added!', category='success')
               return self.redirect('authors')

           return self.render('authors', authors=self.author_manager.all(), form=form)

       @route('/authors/<int:id>')
       @param_converter(id=models.Author)
       def author(self, author):
           return self.render('author', author=author)

       @route(methods=['GET', 'POST'])
       def themes(self):
           form = forms.ThemeForm()
           if form.validate_on_submit():
               theme = form.make_instance()
               self.theme_manager.save(theme, commit=True)
               self.flash('New theme added!', category='success')
               return self.redirect('themes')

           return self.render('themes', themes=self.theme_manager.all(), form=form)

       @route('/themes/<int:id>')
       @param_converter(id=models.Theme)
       def theme(self, theme):
           return self.render('theme', theme=theme)

Templates
^^^^^^^^^

We'll start by adding a macro to render a list of quotes using the html ``blockquote`` tag. This will be  reused everywhere we want to list the quotes associated with a model.

.. code:: html+jinja

   {# app/templates/site/_macros.html #}

   {% macro quote_list(quotes) %}
     {% for quote in quotes %}
       <blockquote>
         {{ quote.quote }}
         <figcaption>&mdash; <cite>{{ quote.author.name }}</cite></figcaption>
       </blockquote>
     {% endfor %}
   {% endmacro %}

quotes.html
~~~~~~~~~~~

This is a simple list of all the quotes in the database.

.. code:: html+jinja

   {# app/templates/site/quotes.html #}

   {% extends "layout.html" %}

   {% from '_macros.html' import render_form %}
   {% from 'site/_macros.html' import quote_list %}

   {% block title %}Quotes{% endblock %}

   {% block content %}
     <h1>Quotes</h1>

     <h2>Add Quote</h2>
     {{ render_form(form) }}
     <hr/>

     {{ quote_list(quotes) }}
   {% endblock %}

authors.html
~~~~~~~~~~~~

For the list of authors, it's just a list of links to the details page for each author. If you wanted to add some more content to this page, a good exercise might be to add a short bio for each author.

.. code:: html+jinja

   {# app/templates/site/authors.html #}

   {% extends 'layout.html' %}

   {% from '_macros.html' import render_form %}

   {% block title %}Authors{% endblock %}

   {% block content %}
     <h1>Authors</h1>

     <h2>Add Author</h2>
     {{ render_form(form) }}
     <hr/>

     <ul>
     {% for author in authors %}
       <li>
         <a href="{{ url_for('site_controller.author', id=author.id) }}">
           {{ author.name }}
         </a>
       </li>
     {% endfor %}
     </ul>
   {% endblock %}

author.html
~~~~~~~~~~~

The detail view for each author lists their quotes. A good exercise might be to show the top three themes found within the author's quotes.

.. code:: html+jinja

   {# app/templates/site/author.html #}

   {% extends 'layout.html' %}

   {% from 'site/_macros.html' import quote_list %}

   {% block title %}{{ author.name }} Quotes{% endblock %}

   {% block content %}
     <h1>{{ author.name }} Quotes</h1>
     {{ quote_list(author.quotes) }}
   {% endblock %}

themes.html
~~~~~~~~~~~

The list of themes is quite similar to the list of authors.

.. code-block:: html+jinja

   {# app/templates/site/themes.html #}

   {% extends 'layout.html' %}

   {% from '_macros.html' import render_form %}

   {% block title %}Themes{% endblock %}

   {% block content %}
     <h1>Themes</h1>

     <h2>Add Theme</h2>
     {{ render_form(form) }}
     <hr/>

     <ul>
     {% for theme in themes %}
       <li>
         <a href="{{ url_for('site_controller.theme', id=theme.id) }}">
           {{ theme.name }}
         </a>
       </li>
     {% endfor %}
     </ul>
   {% endblock %}

theme.html
~~~~~~~~~~

And the theme details page is likewise quite similar to the author detail page.

.. code-block:: html+jinja

   {# app/templates/site/theme.html #}

   {% extends 'layout.html' %}

   {% from 'site/_macros.html' import quote_list %}

   {% block title %}{{ theme.name }} Quotes{% endblock %}

   {% block content %}
     <h1>{{ theme.name }} Quotes</h1>

     {% if theme.description %}
       <p>{{ theme.description }}</p>
     {% endif %}

     {{ quote_list(theme.quotes) }}
   {% endblock %}

Lastly, we also want to update the navbar so that users can easily get to our views:

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
     </div>
   </nav>

Next up we'll continue to :doc:`09_admin_interface`.
