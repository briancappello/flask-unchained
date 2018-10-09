# Flask Unchained

## The better way to build large Flask apps

Flask Unchained aims to provide a fully integrated, optional-batteries-included MVC web framework built on top of Flask and its extension ecosystem. It provides a Flask extension that implements the Application Factory Pattern, utilizing a standardized (but configurable) way to organize "bundles" of code, such that they become easily distributable, reusable, and customizable across multiple independent Flask Unchained projects. The focus is on developer productivity and enjoyment, and the architecture is inspired by [Symfony](https://symfony.com/), which is awesome, aside from the fact that it isn't Python ;)

**WARNING: This software is currently in Alpha.** At this point I feel pretty confident that the core API is pretty solid and shouldn't see too many breaking changes going forward, if at all. But that said, this code hasn't seen widespread production use yet, and it very well may eat your data or servers or worse. You've been warned.

## Useful Links

* [Documentation on Read the Docs](https://flask-unchained.readthedocs.io/en/latest/)
* [Source Code on GitHub](https://github.com/briancappello/flask-unchained)
* [PyPI](https://pypi.org/project/Flask-Unchained/)

## Features

* includes out-of-the-box (mostly optional) integrations with:
   - [Flask-BabelEx](https://pythonhosted.org/Flask-BabelEx/) (translations, required)
   - [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/) (forms and CSRF protection, required)
   - [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/latest/) and [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) (database ORM and migrations, optional)
   - [Flask-Login](http://flask-login.readthedocs.io/) and [Flask-Principal](https://pythonhosted.org/Flask-Principal/) (authentication and authorization, optional)
   - [Flask-Mail](https://pythonhosted.org/flask-mail/) (email sending support, optional)
   - [Flask-Marshmallow](https://flask-marshmallow.readthedocs.io/en/latest/) (SQLAlchemy model serialization, optional)
   - [Flask-Session](https://pythonhosted.org/Flask-Session/) (server-side sessions, optional)
   - [Flask-Admin](https://flask-admin.readthedocs.io/en/latest/) (admin interface, optional)
   - [Celery](http://docs.celeryproject.org/en/latest/index.html) (distributed task queue, optional)
* out-of-the-box support for testing with [pytest](https://docs.pytest.org/en/latest/)
* improved class-based views with the [Controller](https://flask-unchained.readthedocs.io/en/latest/api/bundles/controller.html#controller), [Resource](https://flask-unchained.readthedocs.io/en/latest/api/bundles/controller.html#resource), and [ModelResource](https://flask-unchained.readthedocs.io/en/latest/api/bundles/api.html#modelresource) base classes
* declarative routing
* dependency injection of services and extensions
* a REST API framework, integrated with Marshmallow and SQLAlchemy
   - work-in-progress support for [OpenAPI](https://swagger.io/specification/) (aka Swagger) docs, using [ReDoc](https://github.com/Rebilly/ReDoc) as the frontend (internally, it uses the [APISpec](http://apispec.readthedocs.io/en/stable/) library)
* automatic discovery and registration of:
   - Configuration
   - Controllers, Resources, and Views
   - Services and Extensions
   - Click groups and commands
   - SQLAlchemy database models
   - Marshmallow serializers (aka schemas)
   - Flask-Admin admin classes
   - Celery tasks
* much simplified customization of third-party code

## Quickstart

```bash
#> create a virtual environment
pip install flask-unchained[dev]
flask new project <your-project-folder-name>

# (answer the questions and `cd` into the new directory)
pip install -r requirements-dev.txt
flask run
```

## What does it look like?

Unlike stock Flask, Flask Unchained apps cannot be written in a single file. Instead, we've defined a (configurable) folder convention that must be followed for Flask Unchained to be able to correctly discover all of your code. A minimal Hello World application structure looks like this:

```
/home/user/dev/project-root
├── app
│   ├── templates
│   │   └── site
│   │       └── index.html
│   ├── __init__.py
│   ├── config.py
│   ├── routes.py
│   └── views.py
└── unchained_config.py
```

And a larger application structure might look like this:

```
/home/user/dev/project-root
├── app                 # your app bundle package
│   ├── admins          # model admins
│   ├── commands        # Click groups/commands
│   ├── extensions      # Flask extensions
│   ├── models          # SQLAlchemy models
│   ├── serializers     # Marshmallow serializers (aka schemas)
│   ├── services        # dependency-injectable services
│   ├── tasks           # Celery tasks
│   ├── templates       # Jinja2 templates
│   ├── views           # Controllers and Resources
│   └── __init__.py
│   └── config.py       # app config
│   └── routes.py       # declarative routes
├── assets              # static assets to be handled by Webpack
│   ├── images
│   ├── scripts
│   └── styles
├── bundles             # third-party bundle extensions/overrides
│   └── security        # a customized/extended Flask Security Bundle
│       ├── models
│       ├── serializers
│       ├── services
│       ├── templates
│       └── __init__.py
├── db
│   ├── fixtures        # SQLAlchemy model fixtures (for seeding the dev db)
│   └── migrations      # Alembic migrations (generated by Flask-Migrate)
├── static              # static assets (Webpack compiles to here, and Flask
│                       #  serves this folder at /static (by default))
├── templates           # the top-level templates folder
├── tests               # your pytest tests
├── webpack             # Webpack configs
└── unchained_config.py # the flask unchained config
```

To learn how to build such a larger example application, check out the [official tutorial](https://flask-unchained.readthedocs.io/en/latest/tutorial/index.html).

Going back to the minimal hello world app, the code is as follows:

The first step is to create an app bundle module in your project root, we'll call ours `app`, with an `AppBundle` subclass in it:

```python
# project-root/app/__init__.py

from flask_unchained import AppBundle


class App(AppBundle):
    pass
```

Add the minimal required configuration:

```python
# project-root/app/config.py

import os

from flask_unchained import AppConfig


class Config(AppConfig):
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'change-me-to-a-secret-key')
```

And a hello world view along with its template:

```python
# project-root/app/views.py

from flask_unchained import Controller, route


class SiteController(Controller):
    @route('/')
    def index(self):
        return self.render('index')
```

```html
<!-- project-root/app/templates/site/index.html -->

<!DOCTYPE html>
<html>
<head>
    <title>Hello World from Flask Unchained!</title>
</head>
<body>
    <h1>Hello World from Flask Unchained!</h1>
</body>
</html>
```

Now we can register the controller with our `routes`:

```python
# project-root/app/routes.py

from flask_unchained import (controller, resource, func, include, prefix,
                             get, delete, post, patch, put, rule)

from .views import SiteController


routes = lambda: [
    controller(SiteController),
]
```

Enable the bundle in `unchained_config.py`:

```python
# project-root/unchained_config.py

BUNDLES = [
    'app',
]
```

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
