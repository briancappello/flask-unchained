Views, Templates, and Static Assets
-----------------------------------

So far we've been returning a raw string from our view function. This works fine for demo purposes, however, in the real world you'll most often use template files. Let's create a directory each for our templates and static assets.

.. code:: bash

   mkdir -p templates static \
     && touch templates/layout.html templates/_navbar.html templates/_flashes.html

These directories are the standard locations the :class:`~flask.Flask` constructor expects, so they will automatically be used. (Note however that if just created either of these directories, then you will need to restart the development server for them to be picked up by it.)

Our site looks pretty weak as it stands. Let's add Bootstrap to spruce things up a bit:

.. code:: bash

   && wget https://stackpath.bootstrapcdn.com/bootstrap/4.1.2/js/bootstrap.min.js -O static/bootstrap-v4.1.2.min.js \
     && wget https://stackpath.bootstrapcdn.com/bootstrap/4.1.2/css/bootstrap.min.css -O static/bootstrap-v4.1.2.min.css \
     && wget https://code.jquery.com/jquery-3.3.1.slim.min.js -O static/jquery-v3.3.1.slim.min.js \
     && wget https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js -O static/popper-v1.14.3.min.js \

Layout Template
^^^^^^^^^^^^^^^
In order to share as much code as possible between templates, it's best practice to abstract away the shared boilerplate into ``templates/layout.html``. Just like vanilla Flask, Flask Unchained uses the Jinja2 templating engine. If you're unfamiliar with what anything below is doing, I recommend checking out the exeellent `official Jinja2 documentation <jinja.pocoo.org/docs/>`_.

Now let's write our ``templates/layout.html`` file:

.. code:: html+jinja

   {# templates/layout.html #}

   <!DOCTYPE html>
   <html lang="en">
     <head>
       <meta charset="utf-8">
       <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

       <title>{% block title %}Hello Flask Unchained!{% endblock %}</title>

       {% block stylesheets %}
         <link rel="stylesheet" href="{{ url_for('static', filename='bootstrap-v4.1.2.min.css') }}">
       {% endblock stylesheets %}

       {% block extra_head %}
       {% endblock extra_head %}
     </head>

     <body>
       {% block header %}
         <header>
           {% block navbar %}
             {% include '_navbar.html' %}
           {% endblock %}
         </header>
       {% endblock%}

       {% block body %}
         <div class="container">
           {% include '_flashes.html' %}
           {% block content %}
           {% endblock content %}
         </div>
       {% endblock body %}

       {% block javascripts %}
         <script src="{{ url_for('static', filename='jquery-v3.3.1.slim.min.js') }}"></script>
         <script src="{{ url_for('static', filename='popper-v1.14.3.min.js') }}"></script>
         <script src="{{ url_for('static', filename='bootstrap-v4.1.2.min.js') }}"></script>
       {% endblock javascripts %}
     </body>
   </html>

And also the included  ``templates/_flashes.html`` and ``templates/_navbar.html`` templates:

.. code:: html+jinja

   {# templates/_flashes.html #}

   {% with messages = get_flashed_messages(with_categories=True) %}
   {% if messages %}
     <div class="row flashes">
       <div class="col">
         {% for category, message in messages %}
           <div class="alert alert-{{ category }} alert-dismissable fade show" role="alert">
             {{ message }}
             <button type="button" class="close" data-dismiss="alert" aria-label="Close">
               <span aria-hidden="true">&times;</span>
             </button>
           </div>
         {% endfor %}
       </div>
     </div>
   {% endif %}
   {% endwith %}

.. code:: html+jinja

   {# templates/_navbar.html #}

   {% macro nav_link(label) %}
     {% set href = kwargs.get('href', url_for(kwargs['endpoint'])) %}
     <li class="nav-item {% if kwargs is active %}active{% endif %}">
       <a class="nav-link" href="{{ href }}">
         {{ label }}
         {% if kwargs is active %}
           <span class="sr-only">(current)</span>
         {% endif %}
       </a>
     </li>
   {% endmacro %}

   <nav class="navbar navbar-expand-md navbar-dark bg-dark">
     <a class="navbar-brand" href="{{ url_for('site_controller.index') }}">
       Hello Flask Unchained
     </a>
     <button type="button"
             class="navbar-toggler"
             data-toggle="collapse"
             data-target="#navbarCollapse"
             aria-controls="navbarCollapse"
             aria-expanded="false"
             aria-label="Toggle navigation"
     >
       <span class="navbar-toggler-icon"></span>
     </button>
     <div class="collapse navbar-collapse" id="navbarCollapse">
       <ul class="navbar-nav mr-auto">
         {{ nav_link('Home', endpoint='site_controller.index') }}
       </ul>
     </div>
   </nav>

The ``nav_link`` macro perhaps deserves some explanation. This is a small utility function that renders a navigation item in the bootstrap navbar. We do this to make our code more DRY, because every navigation link needs to contain logic to determine whether or not it is the currently active view. The ``{% if endpoint is active %}`` bit is special - Flask Unchained adds the ``active`` template test by default to make this easier.

And now let's update our ``app/templates/site/index.html`` template to use our new layout template:

.. code:: html+jinja

   {# app/templates/site/index.html #}

   {% extends 'layout.html' %}

   {% block title %}Hello World!{% endblock %}

   {% block content %}
     <div class="row">
       <div class="col">
         <h1>Hello World!</h1>
       </div>
     </div>
   {% endblock %}

Tests should still pass...

.. code:: bash

   pytest
   =================================== test session starts ====================================
   platform linux -- Python 3.6.6, pytest-3.6.4, py-1.5.4, pluggy-0.7.1
   rootdir: /home/user/dev/hello-flask-unchained, inifile:
   plugins: flask-0.10.0, Flask-Unchained-0.8.0
   collected 1 item

   tests/app/test_views.py .                                                             [100%]

   ================================= 1 passed in 0.10 seconds =================================

This seems like a good place to make a commit:

.. code:: bash

   git add .
   git status
   git commit -m 'refactor templates to extend a base layout template'

Customizing Styles
^^^^^^^^^^^^^^^^^^

If you take a look at how our new template looks, it's pretty good, but the ``h1`` tag is now very close to the navbar. Let's fix that by adding some style customizations:

.. code:: bash

   mkdir static/vendor \
      && mv static/*.min.* static/vendor \
      && touch static/main.css

Let's update the ``stylesheets`` and ``javascripts`` blocks in our layout template to reference the changed locations of the vendor assets, and our new ``main.css`` stylesheet:

.. code:: html+jinja

   {# templates/layout.html #}

   {% block stylesheets %}
     <link rel="stylesheet" href="{{ url_for('static', filename='vendor/bootstrap-v4.1.2.min.css') }}">
     <link rel="stylesheet" href="{{ url_for('static', filename='main.css') }}">
   {% endblock stylesheets %}

   {% block javascripts %}
     <script src="{{ url_for('static', filename='vendor/jquery-v3.3.1.slim.min.js') }}"></script>
     <script src="{{ url_for('static', filename='vendor/popper-v1.14.3.min.js') }}"></script>
     <script src="{{ url_for('static', filename='vendor/bootstrap-v4.1.2.min.js') }}"></script>
   {% endblock javascripts %}

And of course, the custom rule for our ``h1`` tags:

.. code:: css

   /* static/main.css */

   h1 {
     padding-top: 0.5em;
     margin-top: 0.5em;
   }

Let's commit our changes:

.. code:: bash

   git add .
   git status
   git commit -m 'add a custom stylesheet'

Adding a Landing Page
^^^^^^^^^^^^^^^^^^^^^

OK, let's refactor our views so we have a landing page and a separate page for the hello view. We're also going to introduce :meth:`flask_unchained.decorators.param_converter` here so that we can (optionally) customizable the name we're saying hello to via the query string:

.. code:: python

   # app/views.py

   from flask_unchained import Controller, route, param_converter


   class SiteController(Controller):
       @route('/')
       def index(self):
           return self.render('index')

       @route('/hello')
       @param_converter(name=str)
       def hello(self, name=None):
           name = name or 'World'
           return self.render('hello', name=name)

The ``param_converter`` converts arguments passed in via the query string to arguments that get passed to the decorated view function. It can make sure you get the right type via a callable (like here), or as we'll cover later, it can even convert unique identifiers from the URL directly into database models. But that's getting ahead of ourselves.

Now that we've added another view/route, our templates need some work again. Let's update the navbar, move our existing ``index.html`` template to ``hello.html`` (adding support for the ``name`` template context variable), and lastly add a new ``index.html`` template for the landing page.

.. code:: html+jinja

   {# templates/_navbar.html #}

   <ul class="navbar-nav mr-auto">
     {{ nav_link('Home', endpoint='site_controller.index') }}
     {{ nav_link('Hello', endpoint='site_controller.hello') }}  <!-- add this line -->
   </ul>

.. code:: html+jinja

   {# app/templates/site/hello.html #}

   {% extends 'layout.html' %}

   {% block title %}Hello {{ name }}!{% endblock %}

   {% block content %}
     <div class="row">
       <div class="col">
         <h1>Hello {{ name }}!</h1>
       </div>
     </div>
   {% endblock %}

.. code:: html+jinja

   {# app/templates/site/index.html #}

   {% extends 'layout.html' %}

   {% block body %}
     <div class="jumbotron">
       <div class="container">
         <div class="row">
           <div class="col">
             <h1 class="display-3">Hello Flask Unchained!</h1>
           </div>
         </div>
       </div>
     </div>
   {% endblock %}

We need to update our tests:

.. code:: python

   # tests/app/test_views.py

   class TestSiteController:
       def test_index(self, client, templates):
           r = client.get('site_controller.index')
           assert r.status_code == 200
           assert templates[0].template.name == 'site/index.html'
           assert r.html.count('Hello Flask Unchained!') == 2

       def test_hello(self, client, templates):
           r = client.get('site_controller.hello')
           assert r.status_code == 200
           assert templates[0].template.name == 'site/hello.html'
           assert r.html.count('Hello World!') == 2

       def test_hello_with_name_parameter(self, client, templates):
           r = client.get('site_controller.hello', name='User')
           assert r.status_code == 200
           assert templates[0].template.name == 'site/hello.html'
           assert r.html.count('Hello User!') == 2

A couple things to note here. Most obviously, we added another view, and therefore need to add methods to test it. Also of note is the ``templates`` pytest fixture, which we're using to verify the correct template got rendered for each of the views.

Let's make sure they pass:

.. code:: bash

   pytest
   =================================== test session starts ===================================
   platform linux -- Python 3.6.6, pytest-3.6.4, py-1.5.4, pluggy-0.7.1
   rootdir: /home/user/dev/hello-flask-unchained, inifile:
   plugins: flask-0.10.0, Flask-Unchained-0.8.0
   collected 3 items

   tests/app/test_views.py ...                                                          [100%]

   ================================ 3 passed in 0.17 seconds =================================

Cool. You guessed it, time to make a commit!

.. code:: bash

   git add .
   git status
   git commit -m 'add landing page, parameterize hello view to accept a name'

Adding a Form to the Hello View
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We've parameterized our hello view take a ``name`` argument, however, it's not exactly discoverable by users (unless perhaps they're a developer with good variable naming intuition). One way to improve this is by using a form. First, we'll add a form the old-school way, followed by a refactor to use Flask-WTF form classes.

Let's update our hello template:

.. code:: html+jinja

   {# app/templates/site/hello.html #}

   {% extends 'layout.html' %}

   {% block title %}Hello {{ name }}!{% endblock %}

   {% block content %}
     <div class="row">
       <div class="col">
         <h1>Hello {{ name }}!</h1>

         <h2>Enter your name:</h2>
         <form name="hello_form" action="{{ url_for('site_controller.hello') }}" method="POST">
           {% if error %}
             <ul class="errors">
               <li class="error">{{ error }}</li>
             </ul>
           {% endif %}
           <div class="form-group">
             <label for="name">Name</label>
             <input type="text" id="name" name="name" class="form-control" />
           </div>
           <button type="submit" class="btn btn-primary">Submit</button>
         </form>
       </div>
     </div>
   {% endblock %}

And the corresponding view code:

.. code:: python

   # app/views.py

   # import request from flask_unchained
   from flask_unchained import Controller, request, route, param_converter

   class SiteController(Controller):
       # and update the code for our hello view
       @route('/hello', methods=['GET', 'POST'])
       @param_converter(name=str)
       def hello(self, name=None):
           if request.method == 'POST':
               name = request.form['name']
               if not name:
                   return self.render('hello', error='Name is required.', name='World')
               return self.redirect('hello', name=name)
           return self.render('hello', name=name or 'World')

A wee styling update to also put some spacing above ``h2`` headers:

.. code:: css

   /* static/main.css */

   h1, h2 {
     padding-top: 0.5em;
     margin-top: 0.5em;
   }

And let's fix our tests:

.. code:: python

   # tests/app/test_views.py

   # add this import
   from flask_unchained import url_for

   class TestSiteController:
       # and add this method
       def test_hello_with_form_post(self, client, templates):
           r = client.post('site_controller.hello', data=dict(name='User'))
           assert r.status_code == 302
           assert r.path == url_for('site_controller.hello')

           r = client.follow_redirects(r)
           assert r.status_code == 200
           assert r.html.count('Hello User!') == 2

           # note: when request is a POST, the templates fixture only works after redirecting
           assert templates[0].template.name == 'site/hello.html'

Make sure they pass,

.. code:: bash

   pytest
   ================================== test session starts ===================================
   platform linux -- Python 3.6.6, pytest-3.7.1, py-1.5.4, pluggy-0.7.1
   rootdir: /home/user/dev/hello-flask-unchained, inifile:
   plugins: flask-0.10.0, Flask-Unchained-0.8.0
   collected 4 items

   tests/app/test_views.py ....                                                        [100%]

   ================================ 4 passed in 0.16 seconds ================================

And commit our changes once satisfied:

.. code:: bash

   git add .
   git status
   git commit -m 'add a form to the hello view'

Converting to a Flask-WTF Form
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The above method works, as far as it goes, but both our view code and our template code are very verbose, and the form verification/error handling is awfully manual. Luckily the Flask ecosystem has a solution to this problem, in the awesomely named ``Flask-WTF`` package (it's installed by default as a dependency of Flask Unchained). With it, our new form looks like this:

.. code:: bash

   touch app/forms.py

.. code:: python

   # app/forms.py

   from flask_unchained.forms import FlaskForm, fields, validators


   class HelloForm(FlaskForm):
       name = fields.StringField('Name', validators=[
           validators.DataRequired('Name is required.')])
       submit = fields.SubmitField('Submit')

The updated view code:

.. code:: python

   # app/views.py

   from flask_unchained import Controller, request, route, param_converter

   from .forms import HelloForm


   class SiteController(Controller):
       @route('/')
       def index(self):
           return self.render('index')

       @route('/hello', methods=['GET', 'POST'])
       @param_converter(name=str)
       def hello(self, name=None):
           form = HelloForm(request.form)
           if form.validate_on_submit():
               return self.redirect('hello', name=form.name.data)
           return self.render('hello', hello_form=form, name=name or 'World')

And the updated template:

.. code:: html+jinja

   {# app/templates/site/hello.html #}

   {% extends 'layout.html' %}

   {% from '_macros.html' import render_form %}

   {% block title %}Hello {{ name }}!{% endblock %}

   {% block content %}
     <div class="row">
       <div class="col">
         <h1>Hello {{ name }}!</h1>

         <h2>Enter your name:</h2>
         {{ render_form(hello_form, endpoint='site_controller.hello') }}
       </div>
     </div>
   {% endblock %}

What is this mythical ``render_form`` macro? Well, we need to write it ourselves. But luckily once it's written, it should work on the majority of :class:`FlaskForm` subclasses. Here's the code for it:

.. code:: bash

   touch templates/_macros.html

.. code:: html+jinja

   {% macro render_form(form) %}
     {% set action = kwargs.get('action', url_for(kwargs['endpoint'])) %}
     <form name="{{ form._name }}" {% if action %}action="{{ action }}"{% endif %} method="POST">
       {{ render_errors(form.errors.get('_error', [])) }}
       {% for field in form %}
         {{ render_field(field) }}
       {% endfor %}
     </form>
   {% endmacro %}

   {% macro render_field(field) %}
     {% set input_type = field.widget.input_type %}

     {# hidden fields #}
     {% if input_type == 'hidden' %}
       {{ field(**kwargs)|safe }}

     {# submit buttons #}
     {% elif input_type == 'submit' %}
       <div class="form-group">
         {{ field(class='btn btn-primary', **kwargs)|safe }}
       </div>

     {# form fields #}
     {% else %}
       <div class="form-group">

         {# checkboxes #}
         {% if input_type == 'checkbox' %}
           <label for="{{ field.id }}">
             {{ field(**kwargs)|safe }} {{ field.label.text }}
           </label>

         {# all other form fields #}
         {% else %}
           {{ field.label }}
           {{ field(class='form-control', **kwargs)|safe }}
         {% endif %}

         {# always render description and/or errors if they are present #}
         {% if field.description %}
           <small class="form-text text-muted form-field-description">
             {{ field.description }}
           </small>
         {% endif %}
         {{ render_errors(field.errors) }}

       </div>  {# /.form-group #}
     {% endif %}
   {% endmacro %}

   {% macro render_errors(errors) %}
     {% if errors %}
       <ul class="errors">
       {% for error in errors %}
         <li class="error">{{ error }}</li>
       {% endfor %}
       </ul>
     {% endif %}
   {% endmacro %}

More complicated forms, for example those with multiple submit buttons or multiple pages, that require more manual control over the presentation can use ``render_field`` directly for each field in the form.

As usual, let's update our tests and make sure they pass:

.. code:: python

   # tests/app/test_views.py

   class TestSiteController:
       # add this method
       def test_hello_errors_with_empty_form_post(self, client, templates):
           r = client.post('site_controller.hello')
           assert r.status_code == 200
           assert templates[0].template.name == 'site/hello.html'
           assert r.html.count('Name is required.') == 1

.. code:: bash

   pytest
   ================================== test session starts ===================================
   platform linux -- Python 3.6.6, pytest-3.7.1, py-1.5.4, pluggy-0.7.1
   rootdir: /home/user/dev/hello-flask-unchained, inifile:
   plugins: flask-0.10.0, Flask-Unchained-0.8.0
   collected 5 items

   tests/app/test_views.py .....                                                       [100%]

   ================================ 5 passed in 0.19 seconds ================================

Once your tests are passing, it's time to make commit:

.. code:: bash

   git add .
   git status
   git commit -m 'refactor hello form to use flask-wtf'

Enabling CSRF Protection
^^^^^^^^^^^^^^^^^^^^^^^^

By default, CSRF protection is disabled. However, any time you're using forms or have enabled authentication (covered later), you should also enable CSRF protection. There are two requirements:

The first is to update our configuration:

.. code:: bash

   touch app/config.py

.. code:: python

   # app/config.py

   from flask_unchained import AppBundleConfig

   class Config(AppBundleConfig):
       SECRET_KEY = 'some-secret-key'
       WTF_CSRF_ENABLED = True

   class TestConfig(Config):
       WTF_CSRF_ENABLED = False

And secondly, we need to actually send the CSRF token in the cookie with every response:

.. code:: python

   # app/__init__.py

   from flask_unchained import AppBundle, generate_csrf

   class App(AppBundle):
       def after_init_app(self, app) -> None:
           @app.after_request
           def set_csrf_token_cookie(response):
               if response:
                   response.set_cookie('csrf_token', generate_csrf())
               return response


Tests should still pass, so it's time to make commit:

.. code:: bash

   git add .
   git status
   git commit -m 'enable CSRF protection'

Cool. Let's move on to :doc:`db` in preparation for installing the Security Bundle.
