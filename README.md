# Flask Unchained

## The best way to build Flask apps

**Flask Unchained is a fully integrated, optional-batteries-included web framework for Flask and its extension ecosystem.** Out of the box, it's as minimal as Flask itself. But Flask Unchained apps can also pick and choose "bundles" to enable that integrate Flask extensions: **bundles are just like Django's "apps", except I think you'll find bundles are even more powerful and extensible**. Flask Unchained aims to stay true to the spirit and API of Flask itself, while also enabling you to rapidly building large and complex web apps and GraphQL/REST APIs with Flask.

> The architecture and "developer experience" of how Flask Unchained and its bundles work is inspired by the [Symfony Framework](https://symfony.com/), which is enterprise-level awesome, aside from the fact that it isn't Python ;)

### Hello Flask Unchained

The classic "hello world" app is just as simple as it is with stock Flask:

```python
# hello-flask-unchained/app.py

from flask_unchained import AppBundle, route

class App(AppBundle):
    pass

@route('/')
def index():
    return '<h1>Hello World from Flask Unchained!</h1>'

def test_index(client):
    r = client.get('index')
    assert r.status_code == 200
    assert r.html.count('Hello World from Flask Unchained!') == 1
```

#### Install Flask Unchained and run it:

**NOTE:** The README assumes v0.8 of Flask Unchained, which is not yet released to PyPI. (install from master with `pip install "git+https://github.com/briancappello/flask-unchained.git@master#egg=flask-unchained[dev]"`)

```bash
# create a virtual environment and activate it (other ways work too, eg pipenv)
cd hello-flask-unchained
mkvirtualenv -p /path/to/python3.6+ hello-flask-unchained

# install Flask Unchained
pip install "flask-unchained[dev]"

# start the development server at http://localhost:5000
UNCHAINED_CONFIG="app" flask run

# run tests (NOTE: you may need to deactivate and reactivate your virtual env first)
UNCHAINED_CONFIG="app" pytest app.py
```

Notice that you never actually instantiated the `Flask` app instance yourself. In Flask Unchained, you don't need to! Flask Unchained knows how to do that for you, no matter how complex your code ends up getting. (Technically, in production, you do still need to create the app yourself. But it's just one line of code: `app = flask_unchained.AppFactory().create_app(PROD)`.)

## Table of Contents

* [Useful Links](https://github.com/briancappello/flask-unchained#useful-links)
* [Introduction / Features](https://github.com/briancappello/flask-unchained#introduction--features)
    - [Included Bundles](https://github.com/briancappello/flask-unchained#included-bundles)
* [A "Contact Us" App with SQLAlchemy, HTML forms, and a RESTful API](https://github.com/briancappello/flask-unchained#a-contact-us-app-with-sqlalchemy-html-forms-and-a-rest-api)
* [Building big, complex apps](https://github.com/briancappello/flask-unchained#building-big-complex-apps)
* [Contributing](https://github.com/briancappello/flask-unchained#contributing)
* [License](https://github.com/briancappello/flask-unchained#license)
* [Acknowledgements](https://github.com/briancappello/flask-unchained#acknowledgements)

## Useful Links

* [Read the Docs](https://flask-unchained.readthedocs.io/en/latest/)
* [Fork it on GitHub](https://github.com/briancappello/flask-unchained)
* [Releases on PyPI](https://pypi.org/project/Flask-Unchained/)

## Introduction / Features

- **Python 3.6+**
- designed to be **easy to start with and even easier to quickly grow your app**
- **clean, flexible and declarative application structure that encourages good design patterns** (no circular imports!)
- **no integration headaches between supported bundles**: everything *should* just work (please file issues if not!)
- absolutely **as little boilerplate and plumbing as possible**
- **out-of-the-box support for testing with `pytest` and `factory_boy`**
- **declarative routing** (routes registered with the app are decoupled from the defaults decorated on views)
- **dependency injection of services and extensions** (into just about whatever you want)
- **simple and consistent patterns for customizing, extending, and/or overriding bundles and everything in them** (e.g. configuration, views/controllers/resources, routes, templates, models, serializers, services, extensions, ...)
   - your customizations are easily distributable as a standalone bundle (Python package), which itself then supports the same patterns for customization, ad infinitum

### Included Bundles

| Bundle | Integrations | Comments |
| ------ | ------------ | -------- |
| Controller Bundle | Integrates views, controllers, resources and their routes with Flask. Also integrates the [CSRFProtect](https://flask-wtf.readthedocs.io/en/stable/csrf.html) extension from [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/index.html). The controller bundle is always enabled. | This bundle makes all the other bundles blueprints (conceptually). All the views within bundles are automatically assigned to a `Blueprint` for their bundle, and bundles implement the same public API as `Blueprint` (accessed via the `unchained` extension instance). You as an end user don't ever actually interact with blueprints in Flask Unchained. (Although they will still work in your app bundle to ease porting views.) |
| SQLAlchemy Bundle | [SQLAlchemy](https://www.sqlalchemy.org/) and via [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/), [Alembic](https://alembic.sqlalchemy.org/en/latest/) | SQL Database ORM & Migrations. Possibly the best ORM on the planet. |
| Security Bundle | [Flask-Login](http://flask-login.readthedocs.io/) and [Flask-Principal](https://pythonhosted.org/Flask-Principal/) | Supports HTML and JSON endpoints for login/logout (session and token authentication), and optionally, registration (with optional email confirmation), and change/forgot password functionality. |
| OAuth Bundle | [Flask-OAuthlib](https://flask-oauthlib.readthedocs.io/en/latest/) | OAuth providers are included for Amazon, GitHub, and GitLab. You can also add your own. Integrated with the Security Bundle. |
| Session Bundle | [Flask-Session](https://pythonhosted.org/Flask-Session/) | Server-side sessions, should be used when utilizing the Security Bundle. |
| API Bundle | [Flask-Marshmallow](https://flask-marshmallow.readthedocs.io/en/latest/), [APISpec](https://github.com/marshmallow-code/apispec) and [ReDoc](https://github.com/Rebilly/ReDoc) | RESTful API framework integrating SQLAlchemy and Marshmallow with the Controller Bundle. Inspired by [Flask-smorest](https://github.com/marshmallow-code/flask-smorest). [*The API Bundle as a whole, but especially the integration with APISpec/ReDoc, is a WIP. That said, JSON APIs already work quite well.*] |
| Graphene Bundle | [Flask-GraphQL](https://github.com/graphql-python/flask-graphql) and [Graphene](https://docs.graphene-python.org/en/latest/) | Integrates Graphene with SQLAlchemy |
| Celery Bundle | [Celery](http://docs.celeryproject.org/en/latest/index.html) | Distributed Task Queue (for running asynchronous/long-running jobs in the background) |
| Babel Bundle | [Flask-BabelEx](https://pythonhosted.org/Flask-BabelEx/) | Translations / Internationalization support (always enabled, optional) |
| Mail Bundle | [Flask-Mail](https://pythonhosted.org/flask-mail/) | Flask Mail uses SMTP to send emails. But you can easily configure a custom `MAIL_SEND_FN` to send emails using an API service such as SendGrid or MailGun. |
| Admin Bundle | [Flask Admin](https://flask-admin.readthedocs.io/en/latest/) | The very basics work. But this bundle needs a lot of work if it's going to compete with Django's admin. (Which itself has its own laundry list of issues, but I digress.) |

**NOTE:** Some bundles are still a work-in-progress. **Parts of the documentation need improvement or are missing.** (What would you like to know how to do but that isn't obvious? Raise an issue!) **Some of the code is still alpha-quality. It works for me, but there are undoubtedly bugs lurking, especially around the edges, and some parts of the API are potentially subject to change.**

## A "Contact Us" App with SQLAlchemy, HTML forms, and a REST API

First create a directory structure to work with:

```
/home/user/dev/hello-flask-unchained
├── app.py
├── static  # just like Flask, this is the default and gets used automatically if it exists
│   └── styles.css
└── templates  # just like Flask, this is the default and gets used automatically if it exists
    ├── layout.html
    └── site
        ├── index.html
        ├── say_hello.html
        └── contact_thanks.html
```

Install new dependencies:

```bash
$ cd hello-flask-unchained
$ pip install "flask-unchained[api,sqlalchemy]"
$ export UNCHAINED_CONFIG="app"
```

And the code:

```python
# hello-flask-unchained/app.py

import os
from http import HTTPStatus
from flask_unchained import AppBundle, AppBundleConfig, FlaskUnchained, Response
from flask_unchained import Controller, param_converter, request, route
from flask_unchained import injectable, generate_csrf
from flask_unchained.cli import cli, click, print_table
from flask_unchained.forms import fields
from flask_unchained.routes import (controller, resource, func, include, prefix,
                                    get, delete, post, patch, put, rule)

from flask_unchained.bundles.api import ModelResource, ModelSerializer
from flask_unchained.bundles.sqlalchemy import db, ModelForm, ModelManager, BaseQuery as Query

# declare which bundles Flask Unchained should load
BUNDLES = [
    'flask_unchained.bundles.api',
    'flask_unchained.bundles.controller',  # always enabled; optional to list in BUNDLES
    'flask_unchained.bundles.sqlalchemy',
    'app',  # your app bundle *must* be last (and only one bundle listed may subclass AppBundle)
]

# a kwarg for the Flask constructor
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))  # determined automatically, optional

class Config(AppBundleConfig):
    SECRET_KEY = 'super-secret-key'

class DevConfig(Config):  # other env-configs are ProdConfig, StagingConfig and TestConfig
    EXPLAIN_TEMPLATE_LOADING = False  # for when you need to debug what's going on
    WTF_CSRF_ENABLED = False  # makes testing the API endpoints with eg CURL easier
    
    # by default the SQLAlchemy bundle uses `ROOT_PATH/db/<env>.sqlite`, just like this:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(ROOT_PATH, 'db', 'dev.sqlite')}"

class App(AppBundle):
    def before_init_app(self, app: FlaskUnchained) -> None:
        pass

    def after_init_app(self, app: FlaskUnchained) -> None:
        @app.after_request
        def set_csrf_token_cookie(response: Response):
            if response:
                response.set_cookie('csrf_token', generate_csrf())
            return response

class ContactSubmission(db.Model):
    # `class Meta` is optional on models (defaults shown)
    # the string values are column names (or you can set them to None to disable the column)
    class Meta:
        pk = 'id'  # if you defined a primary key column(s) on the model yourself, that's used instead
        created_at = 'created_at'  # you can rename all these across all models in your app
        updated_at = 'updated_at'  # or just rename/disable them per-model as needed

    name = db.Column(db.String(256))  # columns are *not nullable* by default
    email = db.Column(db.String(256))
    message = db.Column(db.Text())

class ContactSubmissionManager(ModelManager):
    class Meta:
        model = ContactSubmission

    def by_newest_first(self) -> Query:
        return self.query.order_by(ContactSubmission.created_at.desc())

class ContactSubmissionForm(ModelForm):
    class Meta:
        model = ContactSubmission
    submit = fields.SubmitField()

# Controller is like flask.View, but supports dependency injection and multiple view methods
class SiteController(Controller):
    # get the app's instance of ContactSubmissionManager injected into us
    contact_submission_manager: ContactSubmissionManager = injectable

    # `class Meta` is optional on controllers, defaults shown
    class Meta:
        # default URL prefix for all controllers is '/' (aka no prefix)
        url_prefix = '/'  # applies to all routes on the controller class
        template_folder = 'site'  # snake_cased class name minus any "controller" suffix

    # routing defaults are added for all undecorated pubic methods on concrete subclasses of Controller
    # so index is automatically assigned a route equivalent to:
    # @route('/index', endpoint='site_controller.index', methods=['GET'])
    def index(self):
        return self.render('index')  # renders site/index.html, as determined by:
                                     # f'{Meta.template_folder}/{arg}.{Meta.template_file_extension}'

    # URL rule defaults to kebab-cased function name when omitted, '/say-hello' here
    @route(methods=['GET', 'POST'])
    def say_hello(self):
        form = ContactSubmissionForm(request.form)
        if form.validate_on_submit():
            contact_submission = self.contact_submission_manager.create(
                name=form.name.data,
                email=form.email.data,
                message=form.message.data,
                commit=True,
            )
            return self.redirect('contact_thanks', id=contact_submission.id)
        return self.render('say_hello', form=form)  # renders site/say_hello.html

    @route('/contact/thanks/<int:id>')
    @param_converter(id=ContactSubmission)  # converts `id` url param to a ContactSubmission model (or 404s)
    def contact_thanks(self, contact_submission: ContactSubmission):
        return self.render('contact_thanks', contact_submission=contact_submission)

class ContactSubmissionSerializer(ModelSerializer):  # a marshmallow.Schema subclass
    class Meta:
        model = ContactSubmission

class ContactSubmissionResource(ModelResource):  # a REST API Resource (extends Controller)
    class Meta:
        model = ContactSubmission

        # the following Meta options are all optional: (defaults shown)
        url_prefix = '/contact-submissions'  # model class name pluralized and kebab-cased
        member_param = '<int:id>'
        # there are default (basic) implementations for all of these methods, or you
        # can implement any method(s) with the same names on your subclass to override
        include_methods = ('list', 'create', 'get', 'delete', 'patch', 'put')
        method_decorators = dict(list=(), create=(), 
                                 get=(), delete=(), patch=(), put=())
        # these serializers (which can be different classes) are set up automatically
        # using the declared model class (or set them manually to override defaults)
        serializer = ContactSubmissionSerializer()
        serializer_create = ContactSubmissionSerializer(context=dict(is_create=True))
        serializer_many = ContactSubmissionSerializer(many=True)

# enable explicit/declarative routing
routes = lambda: [
    # to use the default routes as decorated on the views:
    # controller(SiteController),

    # or to override the defaults:
    controller('/', SiteController, rules=[
        get('/', SiteController.index),  # kwargs not overridden get inherited from defaults, eg
        rule('/say-hi', SiteController.say_hello),  # this stays methods=['GET', 'POST'] while
        get('/thanks/<int:id>', SiteController.contact_thanks),  # using `get()` forces ['GET']
    ]),

    prefix('/api/v1', [
        # all three of these registrations are equivalent
        # resource(ContactSubmissionResource),
        # resource('/contact-submissions', ContactSubmissionResource, member_param='<int:id>'),
        resource('/contact-submissions',
                 ContactSubmissionResource,
                 member_param='<int:id>',
                 rules=[
                     get('/', ContactSubmissionResource.list),
                     post('/', ContactSubmissionResource.create),
                     get('/<int:id>', ContactSubmissionResource.get),
                     patch('/<int:id>', ContactSubmissionResource.patch),
                     put('/<int:id>', ContactSubmissionResource.put),
                     delete('/<int:id>', ContactSubmissionResource.delete),
                 ]),
    ]),
]

# command group name should be the same as the snake_cased app bundle's class name
# or, you can set `command_group_names = ['whatever']` on your `AppBundle` subclass
@cli.group()
def app():
    """App bundle commands"""

@app.command('contact-submissions')
@click.option('--limit', type=int, default=5, help='The max number of results to show.')
def contact_submissions(limit, contact_submission_manager: ContactSubmissionManager = injectable):
    """List contact submissions"""
    contact_submissions = contact_submission_manager.by_newest_first().limit(limit)
    if not contact_submissions:
        click.echo("No contact submissions found.")
        return

    print_table(
        column_names=('id', 'name', 'email', 'message', 'created_at'),
        rows=[(row.id, row.name, row.email, row.message, row.created_at.isoformat())
              for row in contact_submissions],
    )
```

You can list the routes that are registered with Flask:

```bash
$ flask urls
Method(s)  Rule                                  Endpoint                            View                                        Options       
-----------------------------------------------------------------------------------------------------------------------------------------------
      GET  /static/<path:filename>               static                              flask.helpers :: send_static_file           strict_slashes
      GET  /                                     site_controller.index               app :: SiteController.index                 strict_slashes
GET, POST  /say-hi                               site_controller.say_hello           app :: SiteController.say_hello             strict_slashes
      GET  /thanks                               site_controller.contact_thanks      app :: SiteController.contact_thanks        strict_slashes
      GET  /api/v1/contact-submissions/          contact_submission_resource.list    app :: ContactSubmissionResource.list       strict_slashes
     POST  /api/v1/contact-submissions/          contact_submission_resource.create  app :: ContactSubmissionResource.create     strict_slashes
      GET  /api/v1/contact-submissions/<int:id>  contact_submission_resource.get     app :: ContactSubmissionResource.get        strict_slashes
   DELETE  /api/v1/contact-submissions/<int:id>  contact_submission_resource.delete  app :: ContactSubmissionResource.delete     strict_slashes
    PATCH  /api/v1/contact-submissions/<int:id>  contact_submission_resource.patch   app :: ContactSubmissionResource.patch      strict_slashes
      PUT  /api/v1/contact-submissions/<int:id>  contact_submission_resource.put     app :: ContactSubmissionResource.put        strict_slashes
```

Let's add the code for our styles and templates before firing up the dev server:

```css
/* hello-flask-unchained/static/styles.css */

html { box-sizing: border-box; }
*, *:before, *:after { box-sizing: inherit; }

body {
  margin: 0 auto;
  max-width: 50em;
  font-family: "Helvetica", "Arial", sans-serif;
  line-height: 1.5;
  padding: 2em 1em;
  color: #555;
}
h1 {
  color: #333;
}
input, textarea {
    width: 100%;
    margin-bottom: 1rem;
}
```

```jinja2
{# hello-flask-unchained/templates/layout.html #}

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>
      {% block title %}Hello World from Flask Unchained!{% endblock %}
    </title>
    {% block stylesheets %}
      <link href="{{ url_for('static', filename='styles.css') }}" rel="stylesheet" type="text/css" />
    {% endblock %}
  </head>

  <body>
    {% block body %}{% endblock %}
    {% block javascripts %}{% endblock %}
  </body>
</html>
```

```jinja2
{# hello-flask-unchained/templates/site/index.html #}

{% extends "layout.html" %}

{% block body %}
  <h1>Hello World from Flask Unchained!</h1>
  <a href="{{ url_for('site_controller.say_hello') }}">Contact Us</a>
{% endblock body %}
```

```jinja2
{# hello-flask-unchained/templates/site/say_hello.html #}

{% extends 'layout.html' %}

{% block title %}Contact Us{% endblock %}

{% block body %}
  <h1>Contact Us</h1>
  <form name="{{ form._name }}" action="{{ url_for('site_controller.say_hello') }}" method="POST">
    {{ form.hidden_tag() }}
    <div>{{ form.name.label('Your name:') }} {{ form.name() }}</div>
    <div>{{ form.email.label('Email Address:') }} {{ form.email() }}</div>
    <div>{{ form.message.label('Message:') }} {{ form.message() }}</div>
    {{ form.submit() }}
  </form>
  <a href="{{ url_for('site_controller.index') }}">Back to homepage</a>
{% endblock body %}
```

```jinja2
{# hello-flask-unchained/templates/site/contact_thanks.html #}

{% extends "layout.html" %}

{% block title %}Thanks for contacting us!{% endblock %}

{% block body %}
  <h1>Thanks for contacting us!</h1>
  <table>
    <tbody>
      <tr><th>Name</th><td>{{ contact_submission.name }}</td></tr>
      <tr><th>Email</th><td>{{ contact_submission.email }}</td></tr>
      <tr><th>Message</th><td>{{ contact_submission.message }}</td></tr>
    </tbody>
  </table>
  <a href="{{ url_for('site_controller.index') }}">Back to homepage</a>
{% endblock body %}
```

Run database migrations, start the development server, and we have liftoff!

```bash
flask db init
flask db migrate -m 'create contact_submission table'
flask db upgrade
flask run
```

We could just have easily split this up into separate modules within an app bundle package:

```
/home/user/dev/hello-flask-unchained
├── unchained_config.py  # Flask kwargs and the BUNDLES list live here
├── static
│   └── styles.css
├── templates  # top-level templates is always searched first for matches
│   └── layout.html
└── app  # the "app" Python package is still our bundle's module name  
    ├── __init__.py  # the App subclass of AppBundle goes here
    ├── commands.py
    ├── config.py
    ├── forms.py
    ├── models.py
    ├── routes.py
    ├── serializers.py
    ├── services.py
    ├── views.py
    └── templates  # if no match in root templates folder, bundles' folders are searched next
        └── site
            ├── index.html
            ├── say_hello.html
            └── contact_thanks.html
```

The directory structure and module names shown above are the defaults but it's all configurable per-bundle. You can use the `flask new project` command to generate this folder structure for you.

You can also *experiment* with splitting things out piece-meal instead of moving everything around at once. For example to split out just the views and templates: (but please see warning below)

```python
class App(AppBundle):
    # when the app bundle isn't a single file, the defaults assume individual modules for everything
    # to only split out views, need to tell Flask Unchained that everything else is in __init__
    config_module_name = '__init__'           # defaults to 'config'
    routes_module_name = '__init__'           # defaults to 'routes'
    commands_module_names = ['__init__']      # defaults to ['commands']
    models_module_names = ['__init__']        # defaults to ['models']
    serializers_module_names = ['__init__']   # defaults to ['serializers']
    services_module_names = ['__init__']      # defaults to ['services']
    views_module_names = ['views']            # the default
    # modules don't have to be top-level, eg: ['views.controllers', 'views.resources']    
    model_resources_module_names = ['views']  # the default

# or you can do the opposite:
class App(AppBundle):
    # set a default
    default_load_from_module_name = '__init__'  # set to None to go back to the above default behavior
    # and customize only what you want to live in separate modules
    views_module_names = ['views']
    model_resources_module_names = ['views']
```

**WARNING**: Things work very reliably when the app bundle is a single file, and when everything of the same type (same base class) in bundles is grouped into separate modules/sub-packages. However, you are *probably likely* to hit edge-cases when splitting things up piece-meal. I just haven't played around with it much so it's uncharted territory. The exceptions thrown will have to do with the import order of things, but the error messages will be opaque and appear to have nothing to do with that. Without a solid grasp of Python metaprogramming or the internals of Flask Unchained, they are of the very hard to debug magical type. (My code worked before. All I did was move things around. It's still valid Python. And now it's blowing up!? That kind of "fun" stuff.)

In this example, by moving `SiteController` into its own module, `ContactSubmissionForm` *must also* live in its own module (or in the same module as the views). (This restriction only applies to subclasses of `ModelForm`; regular `FlaskForm` subclasses can live anywhere.)

To figure out which things have app factory hooks that allow customizing the module locations, run `flask unchained hooks`:

```bash
$ flask unchained hooks
Hook Name                  Default Bundle Module(s)  Bundle Module(s) Override Attr       Description
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
register_extensions        extensions                extensions_module_names              Registers extensions found in bundles with the ``unchained`` extension.
models                     models, forms             models_and_model_forms_module_names  Discovers models and model forms.
configure_app              config                    config_module_name                   Updates ``app.config`` with the settings from each bundle.
init_extensions            extensions                extensions_module_names              Initializes extensions found in bundles with the current app.
services                   services                  services_module_names                Registers services for dependency injection.
inject_extension_services  (None)                    (None)                               Injects services into extensions.
commands                   commands                  commands_module_names                Registers commands and command groups from bundles.
routes                     routes                    routes_module_name                   Registers routes.
bundle_blueprints          (None)                    (None)                               Registers a bundle blueprint for each bundle with views and/or template/static folders.
blueprints                 views                     blueprints_module_names              Registers legacy Flask blueprints with the app.
views                      views                     views_module_names                   Allows configuring bundle views modules.
serializers                serializers               serializers_module_names             Registers serializers.
model_resources            views                     model_resources_module_names         Registers ModelResources and configures Serializers on them.
```

Hooks come from both Flask Unchained and your `unchained_config.BUNDLES` list. Therefore, the output of this command varies by which bundles you're using. The output is sorted by the order the hooks run in, top being the first to run.

## Building big, complex apps

Flask Unchained includes a stock Flask extension called simply `Unchained`, that together with the `AppFactory`, `AppFactoryHook`, and `Bundle` base classes implements a pluggable application factory you can hook into to customize the Flask app instance as it's booting up and/or register things with the app.

A larger application structure might look about like this:

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

To learn how to build such an app, check out the [official tutorial](https://flask-unchained.readthedocs.io/en/latest/tutorial/index.html). (**NOTE:** The tutorial is still a work-in-progress, but is none-the-less currently the best source of "high level" documentation on Flask Unchained.) Most of the APIs are documented as well, but in the end like always, the best source of truth is usually the source code itself. You can also check out [Flask Unchained React SPA](https://github.com/briancappello/flask-unchained-react-spa) for a working example of a (somewhat) bigger REST API built with Flask Unchained and SQLAlchemy.

## Contributing

Contributions are more than welcome! This is a big project with a lot of different things that need doing. There's a TODO file in the project root, or if you've got an idea, open an issue or a PR and let's chat!

## License

MIT

## Acknowledgements

I would like to give a shout out to [factory_boy](https://factoryboy.readthedocs.io/en/latest/), where I discovered [in its source code](https://github.com/FactoryBoy/factory_boy/blob/master/factory/base.py) one of the [metaprogramming patterns](https://github.com/briancappello/py-meta-utils#py-meta-utils) that helps make Flask Unchained so flexible and powerful. It's used throughout Flask Unchained, but notably in the [SQLAlchemy Bundle](https://flask-unchained.readthedocs.io/en/latest/bundles/sqlalchemy.html#usage) (to make all the [`class Meta` options](https://github.com/briancappello/sqlalchemy-unchained#included-meta-options) work). SQLAlchemy Unchained's optional "sugar" (`Meta` options) take inspiration from Django ORM's [`class Meta` options](https://docs.djangoproject.com/en/2.2/ref/models/options/), while the `SessionManager` and `ModelManager` services are inspired by Doctrine's (arguably the best PHP ORM)'s [EntityManager](https://www.doctrine-project.org/api/orm/latest/Doctrine/ORM/EntityManager.html).

I have learned an absolutely incredible amount from the entire Flask ecosystem while building Flask Unchained. It's an incredible community, and I would love to see it continue growing. If you have any feedback or are interested in hacking on Flask Unchained itself, your input would be greatly appreciated!
