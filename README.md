# Flask Unchained

## The best way to build Flask apps

**What is it?**

Flask Unchained is a (*work-in-progress*) **fully integrated, optional-batteries-included web framework built on top of Flask** and its extension ecosystem. Flask Unchained aims to be a fresh, modern take on building web apps and APIs with Flask - while trying to stay as true as possible to the spirit and API of Flask.

**Why?**

- designed to be **easy to start with and even easier to grow** your app
- **clean, predictable application structure** that encourages good design patterns (no circular imports!)
- **documented with real-world-usage in mind** (*some sections are still a work-in-progress*)
- **no integration headaches between supported libraries**; everything just works
- absolutely **as little boilerplate as possible** (your focus should be on your app, not plumbing!)
- out-of-the-box support for **testing** with `pytest`
- **simple and consistent patterns for customizing, extending, and/or overriding almost everything** (e.g. configuration, views/controllers/resources, routes, templates, services, extensions, ...)
   - your customizations are easily distributable as a standalone bundle (Python package), which itself then supports the same patterns for customization, ad infinitum.

**How?**

**Flask Unchained implements the Application Factory Pattern, utilizing a standardized (but configurable) way to organize "bundles" of code, such that they become easily distributable, reusable, and customizable across multiple independent projects.** All of the code within bundles is automatically discovered and registered with the app. You can think of bundles as an enhanced replacement for both Flask blueprints and extensions. Bundles are somewhat comparable to Django's "apps", but I think you'll find bundles are more powerful and flexible.

The architecture is inspired by [Symfony](https://symfony.com/), which is enterprise-level awesome, aside from the fact that it isn't Python ;) If you've heard of [Laravel](https://laravel.com/), that framework is built on top of [the Symfony Components](https://symfony.com/components) - with Flask Unchained, the existing Flask/Python ecosystems constitute our "components".[*]

[*] Don't like the default choices? Flask Unchained is almost completely customizable. The core architecture offers you the potential to use an entirely different stack of libraries, or swap out only certain components - the power to choose is yours.

## Useful Links

* [Read the Docs](https://flask-unchained.readthedocs.io/en/latest/)
* [Fork it on GitHub](https://github.com/briancappello/flask-unchained)
* [Releases on PyPI](https://pypi.org/project/Flask-Unchained/)

### Table of Contents

* [Features](https://github.com/briancappello/flask-unchained#features)
* [Quickstart](https://github.com/briancappello/flask-unchained#quickstart)
* [What does it look like?](https://github.com/briancappello/flask-unchained#what-does-it-look-like)
   * [Application Structure and Project Layout](https://github.com/briancappello/flask-unchained#application-structure-and-project-layout)
   * [Bundles](https://github.com/briancappello/flask-unchained#bundles)
   * [Configuration](https://github.com/briancappello/flask-unchained#configuration)
   * [Views](https://github.com/briancappello/flask-unchained#views)
   * [Templates](https://github.com/briancappello/flask-unchained#templates)
   * [Routes](https://github.com/briancappello/flask-unchained#routes)
   * [Commands](https://github.com/briancappello/flask-unchained#commands)
* [Contributing](https://github.com/briancappello/flask-unchained#contributing)
* [License](https://github.com/briancappello/flask-unchained#license)

## Features

* Python 3.6+
* improved class-based views with the [Controller](https://flask-unchained.readthedocs.io/en/latest/api/controller_bundle.html#controller), [Resource](https://flask-unchained.readthedocs.io/en/latest/api/controller_bundle.html#resource), and [ModelResource](https://flask-unchained.readthedocs.io/en/latest/api/api_bundle.html#modelresource) base classes
* declarative routing
* dependency injection of services and extensions
* includes out-of-the-box (mostly optional) integrations with:
   - [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) (database ORM and migrations, optional). [SQLAlchemy Unchained](https://sqlalchemy-unchained.readthedocs.io/en/latest/) builds some "sugar" on top of SQLAlchemy to make the best ORM in existence even quicker and easier to use:
     - models automatically get a primary key column, unless you define one yourself
     - models are (optionally) automatically timestamped when they are created and updated
     - super-simple polymorphic model class inheritance
     - a unified API for creating, querying, updating and deleting models with the [ModelManager](https://sqlalchemy-unchained.readthedocs.io/en/latest/api.html#modelmanager) service base class
   - [Flask-Login](http://flask-login.readthedocs.io/) (user authentication and sessions management) and [Flask-Principal](https://pythonhosted.org/Flask-Principal/) (user authorization with permissions and roles)
     - both session and token authentication are currently supported
     - includes optional support for registration (with optional required email confirmation before account activation)
     - optional change password and forgot password functionality
   - [Flask-Marshmallow](https://flask-marshmallow.readthedocs.io/en/latest/) (SQLAlchemy model serialization, optional)
      - the API Bundle provides a (*work-in-progress*) RESTful API framework integrating Marshmallow Serializers (aka Schemas) and SQLAlchemy models using [ModelResource](https://flask-unchained.readthedocs.io/en/latest/api/api_bundle.html#modelresource)
      - work-in-progress support for [OpenAPI](https://swagger.io/specification/) (aka Swagger) docs, using [ReDoc](https://github.com/Rebilly/ReDoc) as the frontend
   - [Flask-GraphQL](https://github.com/graphql-python/flask-graphql) (GraphQL support, integrates [Graphene](https://docs.graphene-python.org/en/latest/) with SQLAlchemy, optional)
   - [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/) (forms and CSRF protection, always enabled)
   - [Flask-Session](https://pythonhosted.org/Flask-Session/) (server-side sessions, optional)
   - [Celery](http://docs.celeryproject.org/en/latest/index.html) (distributed task queue, optional)
   - [Flask-Mail](https://pythonhosted.org/flask-mail/) (email sending support, optional)
   - [Flask-Admin](https://flask-admin.readthedocs.io/en/latest/) (admin interface, optional)
   - [Flask-BabelEx](https://pythonhosted.org/Flask-BabelEx/) (translations, always enabled but optional)
   - [pytest](https://docs.pytest.org/en/latest/) and [factory_boy](https://factoryboy.readthedocs.io/en/latest/) (testing framework)

## Quickstart

```bash
# (create a virtual environment)
pip install flask-unchained[dev]
flask new project <your-project-folder-name>

# (answer the questions and `cd` into the new directory)
pip install -r requirements-dev.txt
flask run
```

**NOTE:** If you enabled the SQLAlchemy Bundle, then you may need to run migrations before running the development server:

```bash
flask db init
flask db migrate -m 'create initial tables'
flask db upgrade
```

## What does it look like?

### Application Structure and Project Layout

Unlike stock Flask, Flask Unchained apps cannot be written in a single file. Instead, Flask Unchained's bundles define a (configurable) folder convention that must be followed for Flask Unchained to be able to correctly discover all of your code. A large application structure might look about like this:

```
/home/user/dev/project-root
├── app                 # your app bundle package
│   ├── admins          # model admins
│   ├── commands        # Click CLI groups/commands
│   ├── extensions      # Flask extensions
│   ├── models          # SQLAlchemy models
│   ├── fixtures        # SQLAlchemy model fixtures (for seeding the dev db)
│   ├── serializers     # Marshmallow serializers (aka schemas)
│   ├── services        # dependency-injectable services
│   ├── tasks           # Celery tasks
│   ├── templates       # Jinja2 templates
│   ├── views           # Controllers, Resources and views
│   └── __init__.py
│   └── config.py       # app config
│   └── routes.py       # declarative routes
├── assets              # static assets to be handled by Webpack
│   ├── images
│   ├── scripts
│   └── styles
├── bundles             # custom bundles and/or bundle extensions/overrides
│   └── security        # a customized/extended Security Bundle
│       ├── models
│       ├── serializers
│       ├── services
│       ├── templates
│       └── __init__.py
├── db
│   └── migrations      # Alembic (SQLAlchemy) migrations (generated by Flask-Migrate)
├── static              # static assets (Webpack compiles to here, and Flask
│                       #  serves this folder at /static (by default))
├── templates           # the top-level templates folder
├── tests               # your pytest tests
├── webpack             # Webpack configs
└── unchained_config.py # the Flask Unchained config
```

To learn how to build such a larger example application, check out the [official tutorial](https://flask-unchained.readthedocs.io/en/latest/tutorial/index.html).

A minimal application structure looks about like this:

```
/home/user/dev/hello-flask-unchained
├── app
│   ├── templates
│   │   └── site
│   │       └── index.html
│   ├── __init__.py
│   ├── config.py
│   ├── forms.py
│   ├── models.py
│   ├── routes.py
│   ├── services.py
│   └── views.py
└── unchained_config.py
```

Let's built it!

```bash
# (create a virtualenv and activate it)
pip install flask-unchained[dev,sqlalchemy] \
   && mkdir -p hello-flask-unchained/app && cd hello-flask-unchained \
   && touch unchained_config.py && cd app \
   && mkdir -p templates/site && touch templates/site/index.html \
   && touch __init__.py config.py forms.py models.py routes.py services.py views.py
```

### Bundles

The first step is to create an app bundle module in your project root - we're calling ours `app` here - with an `AppBundle` subclass in it:

```python
# hello-flask-unchained/app/__init__.py

from flask_unchained import AppBundle, FlaskUnchained


class App(AppBundle):
    # you only need to subclass AppBundle; everything below is optional. for example, these
    # attributes can be set to customize which bundle module to load from (defaults shown)
    config_module_name = 'config'
    models_module_name = 'models'
    routes_module_name = 'routes'
    services_module_name = 'services'

    # these two methods are optional callbacks which the app factory will call
    def before_init_app(self, app: FlaskUnchained):
        pass
        
    def after_init_app(self, app: FlaskUnchained):
        pass
```

### Configuration

The configuration for Flask Unchained itself is pretty minimal, for example:

```python
# hello-flask-unchained/unchained_config.py

import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

def folder_or_none(folder_name):
    folder = os.path.join(PROJECT_ROOT, folder_name)
    return folder if os.path.exists(folder) else None

# these get passed to the :class:`FlaskUnchained` constructor
TEMPLATE_FOLDER = folder_or_none('templates')
STATIC_FOLDER = folder_or_none('static')
STATIC_URL_PATH = '/static' if STATIC_FOLDER else None

# declare which bundles Flask Unchained should load
BUNDLES = [
    'flask_unchained.bundles.sqlalchemy',
    'app',  # your app bundle *must* be last
]
```

And add the required app configuration to your app bundle:

```python
# hello-flask-unchained/app/config.py

import os

from flask_unchained import AppBundleConfig


class Config(AppBundleConfig):
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'change-me-to-a-secret-key')


# the following env-specific config classes are all optional

class DevConfig(Config):
    pass

class ProdConfig(Config):
    pass
    
class StagingConfig(ProdConfig):
    pass
```

### Models

```python
# hello-flask-unchained/app/models.py

from flask_unchained.bundles.sqlalchemy import db


class NameSubmission(db.Model):
    class Meta:
        repr = ('id', 'name')

    name = db.Column(db.String(128))

    # the following primary key and timestamp columns are automatically added to models
    # (if necessary/not customized)
    # id = db.Column(db.Integer, primary_key=True)
    # created_at = db.Column(db.DateTime, server_default=sqlalchemy.func.now())
    # updated_at = db.Column(db.DateTime, server_default=sqlalchemy.func.now(),
    #                        onupdate=sqlalchemy.func.now())
```

### Services

```python
# hello-flask-unchained/app/services.py

from flask_unchained.bundles.sqlalchemy import ModelManager

from . import models


class NameSubmissionManager(ModelManager):
    class Meta:
        model = models.NameSubmission

    def create(self, name, commit: bool = False, **kwargs) -> models.NameSubmission:
        return super().create(name=name, commit=commit, **kwargs)
```

### Forms

```python
# hello-flask-unchained/app/forms.py

from flask_unchained.bundles.sqlalchemy.forms import ModelForm

from . import models


class NameSubmissionForm(ModelForm):
    class Meta:
        model = models.NameSubmission
```

### Views

A hello world view:

```python
# hello-flask-unchained/app/views.py

from flask_unchained import Controller, route, request, injectable, param_converter

from . import forms, models, services


class SiteController(Controller):
    name_submission_manager: services.NameSubmissionManager = injectable

    @route('/', methods=['GET', 'POST'])
    @param_converter(id=models.NameSubmission)  # converts the `id` query param to a model
    def index(self, name_submission=None):
        form = forms.NameSubmissionForm(request.form)
        if form.validate_on_submit():
            name_submission = self.name_submission_manager.create(name=form.name.data,
                                                                  commit=True)
            return self.redirect('index', id=name_submission.id)
        return self.render('index', form=form, name_submission=name_submission)
```

### Templates

```jinja2
{# hello-flask-unchained/app/templates/layout.html #}

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>{% block title %}Flask Unchained Hello World{% endblock %}</title>

    {% block stylesheets %}
    {% endblock stylesheets %}
  </head>

  <body>
    {% block body %}
      <div class="container">
        {% block content %}
        {% endblock content %}
      </div>
    {% endblock body %}

    {% block javascripts %}
    {% endblock javascripts %}
  </body>
</html>
```

```jinja2
{# hello-flask-unchained/app/templates/site/index.html #}

{% extends 'layout.html' %}

{% set name = name_submission.name | default('World') %}

{% block title %}Hello {{ name }}{% endblock %}

{% block content %}
  <h1>Hello {{ name }}</h1>

  <form name="{{ form._name }}" action="{{ url_for('site_controller.index') }}" method="POST">
    {{ form.hidden_tag() }}
    {{ form.name.label('Enter your name:') }}
    {{ form.name() }}
    <button type="submit">Submit</button>
  </form>
{% endblock %}
```

### Routes

Now we can register the controller with our `routes`:

```python
# hello-flask-unchained/app/routes.py

from flask_unchained import (controller, resource, func, include, prefix,
                             get, delete, post, patch, put, rule)

from .views import SiteController


routes = lambda: [
    controller(SiteController),
]
```

### Commands

And run it:

```bash
flask run
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

Now you should be able to browse to [http://localhost:5000](http://localhost:5000) to view your new site!

## Contributing

Contributions are more than welcome! This is a big project with a lot of different things that need doing. There's a TODO file in the project root, or if you've got an idea, open an issue or a PR and let's chat.

## License

MIT
