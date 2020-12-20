# Flask Unchained

## The quickest and easiest way to build large web apps and APIs with Flask and SQLAlchemy

**Flask Unchained is a Flask extension, a pluggable application factory, and a set of mostly optional "bundles" that together create a modern, fully integrated, and highly customizable web framework *for* Flask and its extension ecosystem.** Flask Unchained aims to stay true to the spirit and API of Flask, while making it significantly easier to quickly build large web apps and APIs with Flask and SQLAlchemy.

Flask Unchained introduces "bundles" to Flask: bundles are Python packages that integrate functionality with Flask, Flask Unchained, and other bundles. That could mean anything from integrating vanilla Flask extensions to being full-blown apps *your* app can integrate, customize, and extend (like say, a blog or web store). Unlike vanilla Flask extensions, bundles are both consistent and highly extensible and customizable. Once you figure out how something works in one bundle, it's the same in every other bundle. They are conceptually similar to Django's "apps", but I think you'll find bundles are even more powerful and flexible.

> The architecture of how Flask Unchained and its bundles work is inspired by the [Symfony Framework](https://symfony.com/), which is awesome, aside from the fact that it isn't Python ;)

## Features

- easy to start with and even easier to quickly grow your app
- clean, flexible, and declarative application structure that encourages good design patterns (no circular imports!)
- no integration headaches between supported libraries: everything just works
- as little boilerplate/plumbing as possible
- out-of-the-box support for testing with `pytest` and `factory_boy`
- improved class-based views (controllers and resources)
- declarative routing (routes registered with the app can be decoupled from the defaults decorated on views)
- dependency injection of services and extensions (into just about anything you can wrap with a decorator)
- simple and consistent patterns for extending and/or overriding practically everything (e.g. configuration, views/controllers/resources, routes, templates, models, serializers, services, extensions, ...)
   - your customizations are easily distributable as a standalone bundle (Python package), which itself then supports the same patterns for customization, ad infinitum
- out-of-the-box (mostly optional) integrations with:
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
      - the API Bundle provides a RESTful API framework integrating Marshmallow Serializers (aka Schemas) and SQLAlchemy models using [ModelResource](https://flask-unchained.readthedocs.io/en/latest/api/api_bundle.html#modelresource)
      - work-in-progress support for [OpenAPI](https://swagger.io/specification/) (aka Swagger) docs, using [ReDoc](https://github.com/Rebilly/ReDoc) as the frontend
   - [Flask-GraphQL](https://github.com/graphql-python/flask-graphql) (GraphQL support, integrates [Graphene](https://docs.graphene-python.org/en/latest/) with SQLAlchemy, optional)
   - [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/) (forms and CSRF protection, always enabled)
   - [Flask-Session](https://pythonhosted.org/Flask-Session/) (server-side sessions, optional)
   - [Celery](http://docs.celeryproject.org/en/latest/index.html) (distributed task queue, optional)
   - [Flask-Mail](https://pythonhosted.org/flask-mail/) (email sending support, optional)
   - [Flask-Admin](https://flask-admin.readthedocs.io/en/latest/) (admin interface, optional)
   - [Flask-BabelEx](https://pythonhosted.org/Flask-BabelEx/) (translations, always enabled but optional)
   - [pytest](https://docs.pytest.org/en/latest/) and [factory_boy](https://factoryboy.readthedocs.io/en/latest/) (testing framework)
- You can use Flask Unchained as-is with its out-of-the-box "stack", or if you don't like those choices, then you can use a different set of Flask extensions. Flask Unchained is designed to be so flexible that you could even extend it to make your own works-out-of-the-box web framework for Flask.

## What does it look like?

### Hello World

A silly (more verbose than it needs to be) example looks about like this:

```python
# project-root/app.py

import random
from flask_unchained import FlaskUnchained, AppBundle, Service, injectable
from flask_unchained import Controller, route, param_converter, url_for
from flask_unchained.pytest import HtmlTestClient


BUNDLES = ['flask_unchained.bundles.controller']


class App(AppBundle):
    def before_init_app(self, app: FlaskUnchained) -> None:
        pass

    def after_init_app(self, app: FlaskUnchained) -> None:
        pass


class RandomService(Service):
    def get_name(self) -> str:
        return random.choice(['Alice', 'Bob', 'Grace', 'Judy'])


class SiteController(Controller):
    class Meta:
        url_prefix = '/'

    random_service: RandomService = injectable

    @route('/')
    @param_converter(name=str)
    def index(self, name: str = None):
        name = name or self.random_service.get_name()
        return f'Hello {name} from Flask Unchained!'


class TestSiteController:
    def test_index(self, client: HtmlTestClient):
        r = client.get(url_for('site_controller.index', name='World'))
        assert r.status_code == 200
        assert r.html == 'Hello World from Flask Unchained!'
```

You can run it like so:

```bash
pip install "flask-unchained[dev]"
export UNCHAINED="app"
pytest app.py
flask urls
flask run
```

### Going Big

A larger application structure might look about like this:

```
/home/user/dev/project-root
├── app                 # your app bundle package
│   ├── admins          # Flask-Admin model admins
│   ├── commands        # Click CLI groups/commands
│   ├── extensions      # vanilla Flask extensions
│   ├── models          # SQLAlchemy models
│   ├── fixtures        # SQLAlchemy model fixtures (for seeding the dev db)
│   ├── serializers     # Marshmallow serializers (aka schemas)
│   ├── services        # dependency-injectable services
│   ├── tasks           # Celery tasks
│   ├── templates       # Jinja2 templates
│   ├── views           # Controllers, Resources and views
│   ├── __init__.py
│   ├── config.py       # app config
│   └── routes.py       # declarative routes
├── assets              # static assets to be handled by Webpack
│   ├── images
│   ├── scripts
│   └── styles
├── bundles             # custom bundles and/or bundle extensions/overrides
│   └── security        # a customized/extended Security Bundle
│       ├── models
│       ├── serializers
│       ├── services
│       ├── templates
│       └── __init__.py
├── db
│   └── migrations      # Alembic (SQLAlchemy) migrations (generated by Flask-Migrate)
├── static              # static assets (Webpack compiles to here, and Flask
│                       #  serves this folder at /static (by default))
├── templates           # the top-level templates folder
├── tests               # your pytest tests
├── webpack             # Webpack configs
└── unchained_config.py # the Flask Unchained config
```

To learn how to build such an app, check out the [official tutorial](https://flask-unchained.readthedocs.io/en/latest/tutorial/index.html). (**NOTE:** The tutorial is still a work-in-progress.) You can also check out [Flask Unchained React SPA](https://github.com/briancappello/flask-unchained-react-spa)

## Documentation and Tutorial

The docs are on [Read the Docs](https://flask-unchained.readthedocs.io/en/latest/index.html), as is the [official tutorial](https://flask-unchained.readthedocs.io/en/latest/tutorial/index.html).

**NOTE:** Some bundles are still a work-in-progress. Parts of the documentation need improvement or are missing. Some corners of the code are still alpha-quality. Things work for me, but there are probably a few bugs lurking, and some parts of the API are potentially subject to change.

## Contributing

Contributions are more than welcome! This is a big project with a lot of different things that need doing. There's a TODO file in the project root, or if you've got an idea, open an issue or a PR and let's chat!

## License

MIT
