# CHANGELOG

## v0.8.1 (2021/01/17)

### Features

- upgrade Flask-Admin templates to bootstrap4
- add Admin-specific post login/logout redirect endpoints
- add default Model Admins for the User and Role models

### Bug Fixes

- fix default config settings for `ADMIN_LOGIN_ENDPOINT` and `ADMIN_LOGOUT_ENDPOINT`
- defer initialization of the Admin extension to fix template overriding
- do not register duplicate templates folder for single-module app bundle

### Breaking Changes

- rename `User.active` to `User.is_active` for compatibility with Flask-Login v0.5

## v0.8.0 (2020/12/20)

### Features

- **experimental asyncio support by installing [Quart](https://gitlab.com/pgjones/quart)**
- **major improvements to** `AppFactory` **and** `AppFactoryHook`
    - **support single-file app bundles** (just export the app bundle as `UNCHAINED`)
    - support using a custom subclass of `FlaskUnchained` using `AppFactory.APP_CLASS`
    - support using a custom subclass of `AppFactory`
    - support passing all kwargs to `Flask` by setting the same names upper-cased in `unchained_config`
    - support automatic defaults for the Flask app kwargs `root_path`, `template_folder`, `static_folder`, and `static_url_path`
    - support extending and overriding hooks with the same consistent object-oriented patterns
    - support using a custom module name for `unchained_config` by setting the `UNCHAINED` environment variable
    - make it possible to define multiple modules hooks should load from (excluding config and routes, as those only make sense to live inside a single module within bundles)
        - very experimental: add `Bundle.default_load_from_module_name` to ease migration from single-file app bundles to individual modules for different types (ie grouped by base class)
- set up automatic dependency injection on commands (use `from flask_unchained.cli import cli, click` and define command groups for your commands using `@cli.group()`)
- add `flask unchained config` command for listing the current config (optionally filtered by bundle)
- add `flask unchained extensions` command for listing extensions discovered by the app
- add `flask unchaiend services` command for listing services discovered by the app
- alias `flask.abort` (`werkzeug.exceptions.abort`) as `flask_unchained.abort`
- alias `flask_wtf.csrf.generate_csrf` as `flask_unchained.generate_csrf`
- alias `flask.Request` and `flask.Response` into `flask_unchained`
- support `Accept` headers for handling responses in the API bundle
- allow customizing the endpoint prefix for controllers using `Controller.Meta.endpoint_prefix`

### General Improvements

- document the rest of SQLAlchemy's config options
- automatically discover services in the `services` and `managers` modules of bundles
- bump sqlalchemy-unchained to v0.11.0
- add compatibility with pytest 5

### Bug Fixes

- fix grouping routes by which bundle they're from
- fix registration of resource method routes so the order is deterministic
- fix `ConfigureAppHook` to load configs from every bundle in the hierarchy, not just the top-most one
- fix resolving extension initiation order to only happen once instead of twice
- fix passing explicit rule overrides to `routes.resource`
- fix automatic endpoint names for resource routes using the default implementations for create/list/get/delete/patch/put
- fix using default url rule from view function when no explicit rule passed to `func`
- fix `flask urls` command when no URLs found
- make sure hooks don't resolve local proxies
- fix `ModelResource.Meta.url_prefix` to use `Meta.model.__name__` instead of the resource's class name
- allow using `AnonymousUser` as if it were a SQLAlchemy model in queries

### Breaking Changes

- rename `flask_unchained.BaseService` to `flask_unchained.Service`
- rename `PROJECT_ROOT` to `ROOT_PATH` for consistency with upstream `Flask`
- rename `Bundle.folder` to `Bundle.root_path` for consistency with `Flask`
- rename `Controller.Meta.template_folder_name` to `Controller.Meta.template_folder` for consistency with `Flask`
- `AppFactory` is now a `Singleton` that must be instantiated (ie change `AppFactory.create_app(env)` to `AppFactory().create_app(env)` in `wsgi.py`)
- no longer automatically set up dependency injection on all the methods from classes (you can still decorate them manually with `unchained.inject()`, but the preferred approach is to use class attributes to define what to inject into classes)
- default endpoint name for simple view functions is now just the function name
- rename Resource method name constants to reduce confusion with HTTP method names
- remove `AppBundleConfig.ROOT_PATH` and `AppBundleConfig.APP_ROOT` as they didn't always work correctly (use `BundleConfig.current_app.root_path` instead)
- moved `flask_unchained.commands.utils.print_table` to `flask_unchained.cli.print_table`
- if using the API bundle, require `marshmallow>=3.0`, `marshmallow-sqlalchemy>=0.23`, and `flask-marshmallow>=0.12`
- if using the SQLAlchemy bundle, require `sqlalchemy-unchained>=0.10`
- CSRF protection is no longer enabled by default. To re-enable it:

```python
from flask_unchained import BundleConfig, unchained, generate_csrf

class Config(BundleConfig):
    SECRET_KEY = 'some-secret-key'
    WTF_CSRF_ENABLED = True

class TestConfig(Config):
    WTF_CSRF_ENABLED = False

@unchained.after_request
def set_csrf_token_cookie(response):
    if response:
        response.set_cookie('csrf_token', generate_csrf())
    return response
```

- customizing bundle module locations changed:

```python
class YourBundle(Bundle):
    extensions_module_name = 'custom'  # before
    extensions_module_names = ['custom']  # after

    services_module_name = 'custom'  # before
    services_module_names = ['custom']  # after

    commands_module_name = 'custom'  # before
    commands_module_names = ['custom']  # after

    blueprints_module_name = 'custom'  # before
    blueprints_module_names = ['custom']  # after

    models_module_name = 'custom'  # before
    models_module_names = ['custom']  # after

    admins_module_name = 'custom'  # before
    admins_module_names = ['custom']  # after

    resources_module_name = 'custom'  # before
    model_resources_module_names = ['custom']  # after

    serializers_module_name = 'custom'  # before
    model_serializers_module_names = ['custom']  # after

    celery_tasks_module_name = 'custom'  # before
    celery_tasks_module_names = ['custom']  # after

    graphene_queries_module_name = 'custom'  # before
    graphene_queries_module_names = ['custom']  # after

    graphene_mutations_module_name = 'custom'  # before
    graphene_mutations_module_names = ['custom']  # after

    graphene_types_module_name = 'custom'  # before
    graphene_types_module_names = ['custom']  # after
```

### Internals

- move `Bundle` and `AppBundle` into the `flask_unchained.bundles` module
- move `BundleBlueprint` into the `flask_unchained.bundles.controller.bundle_blueprint` module
- move `_DeferredBundleFunctions` into `flask_unchained.unchained`, rename it to `DeferredBundleFunctions`
- make a bunch more protected internal classes public
- make `_has_views`, `_blueprint_names`, `_static_folders`, `is_top_bundle` and `_has_hierarchy_name_conflicts` methods on `Bundle` properties
- rename double-negative `reverse_mro` parameter for `Bundle._iter_class_hierarchy` to `mro`
- warn when identical routes are registered
- make `AppFactory` methods `load_bundles`, `load_bundle` and `is_bundle` classmethods
- add a noop `ViewsHook` to consolidate logic for defining and loading `views_module_names`
- move `param_converter` into the controller bundle

## v0.7.9 (2019/05/19)

- compatibility with `sqlalchemy-unchained >= 0.7.6`

## v0.7.8 (2019/04/21)

- bump required `alembic` version to 1.0.9, fixes `immutabledict is not defined` error

## v0.7.7 (2019/04/11)

- bump requirements
- change behavior of `flask new project` command to use defaults unless `--prompt` is given

- NOTE: broken with sqlalchemy bundle, must install alembic using:

```bash
pip install git+https://github.com/sqlalchemy/alembic.git@d46de05b8b3281a85e6b107ef3f3407e232eb9e9#egg=alembic
```

## v0.7.6 (2019/03/24)

- NOTE: broken with sqlalchemy bundle, must install alembic using:

```bash
pip install git+https://github.com/sqlalchemy/alembic.git@d46de05b8b3281a85e6b107ef3f3407e232eb9e9#egg=alembic
```

## v0.7.5 (2019/03/24)

- NOTE: broken with sqlalchemy bundle, must install alembic using:

```bash
pip install git+https://github.com/sqlalchemy/alembic.git@d46de05b8b3281a85e6b107ef3f3407e232eb9e9#egg=alembic
```

## v0.7.4 (2019/03/17)

- support injecting current app config into services
- extend the `string` url parameter converter to support `upper=True/False`
- add `ModelForm.make_instance` convenience method
- fix `ModelForm.name` to return `bytes`
- add `.gitignore` to `flask new project` command
- improve error message when no `config` module found in the app bundle

## v0.7.3 (2019/02/26)

- do not generate `celery_app.py` for new projects without the celery bundle enabled
- improve user warnings when mail bundle is enabled but lxml or beautifulsoup isn't installed
- bump required versions of py-meta-utils and sqlalchemy-unchained

## v0.7.2 (2019/02/25)

- fix the project's registered name on PyPI so it doesn't contain spaces

## v0.7.1 (2019/02/04)

### Bug fixes

- support multiple routing rules with the same endpoint per view function
- fix type error in dependency injection when comparing parameter values with string

## v0.7.0 (2019/01/30)

### Features

- :fire:OAuth:fire: support with the new OAuth Bundle (many thanks to [@chriamue](https://github.com/chriamue)!)
- :fire:GraphQL:fire: support with the new Graphene Bundle
- add support for specifying parameters to inject into classes as class attributes
- when using `unchained.inject()` on a class, or subclassing a class that supports automatic dependency injection, all non-dunderscore methods now support having dependencies injected
- the `include` function used in `routes.py` now supports specifying the url prefix as the first argument
- support distributing and loading database fixture files with/from bundles
- implement proper support for `ModelForm` (it now adds fields for columns by default)

#### Configuration Improvements

- add a way for bundle configs to get access to the current app-under-construction
- make options in `app.config` accessible as attributes, eg `app.config.SECRET_KEY` is now the same as `app.config['SECRET_KEY']`
- apply any settings from the app bundle config not already present in `app.config` as defaults before loading bundles

### General

- improve documentation of how Flask Unchained works
- update to py-meta-utils 0.7.4 and sqlalchemy-unchained 0.7.0
- update to marshmallow 2.16
- update to marshmallow-sqlalchemy 0.15

### Breaking Changes

- move database fixture loading code into the `py_yaml_fixtures` package (which is now a bundle as of v0.4.0)
- consolidate `unchained.get_extension_local_proxy` and `unchained.get_service_local_proxy` into a single function, `unchained.get_local_proxy`
- rename `AppConfig` to `BundleConfig`
- rename the `SQLAlchemy` extension class to `SQLAlchemyUnchained`
- rename `flask_unchained.bundles.sqlalchemy.model_form` to `flask_unchained.bundles.sqlalchemy.forms`
- rename the Graphene Bundle's `QueryObjectType` to `QueriesObjectType` and `MutationObjectType` to `MutationsObjectType`
- rename the Security Bundle's `SecurityUtilsService.verify_and_update_password` method to `verify_password`
- (internal) descriptors, metaclasses, meta options, and meta option factories are now protected
- (internal) rename the `flask_unchained.app_config` module to `flask_unchained.config`
- (internal) remove the `Bundle.root_folder` descriptor as it made no sense (`Bundle.folder` is the bundle package's root folder)
- (internal) rename `ConfigPropertyMeta` to `ConfigPropertyMetaclass`

### Bug fixes

- fix the `Api` extension so it only generates docs for model resources that are registered with the app
- fix setting of `Route._controller_cls` when controllers extend another concrete controller with routes
- fix `Bundle.static_url_path` descriptor
- specify required minimum package versions in `setup.py`, and pin versions in `requirements.txt`
- fix the `UnchainedModelRegistry.reset` method so it allows using factory_boy from `conftest.py`
- fix the `flask celery` commands so that they gracefully terminate instead of leaving zombie processes running
- fix `param_converter` to allowing converting models from optional query parameters
- add support to graphene for working with SQLAlchemy BigInteger columns

## v0.6.6 (2018/10/09)

- ship `_templates` folder with the distribution so that the `flask new <tempate>` command works when Flask Unchained gets installed via `pip`

## v0.6.0 - v0.6.5 (2018/10/09)

**IMPORTANT:** these releases are broken, use `v0.6.6`

- export `get_boolean_env` from core `flask_unchained` package
- export `param_converter` from core `flask_unchained` package
- fix discovery of user-app `tests._unchained_config`
- improve the output of commands that display their information in a table
- improve the output of custom sqlalchemy types in generated migrations files
- improve the output of the Views column from the `flask urls` command
- improve the `--order-by` option of the `flask urls` command
- rename command `flask db import_fixtures` to `flask db import-fixtures`
- add a `FlaskForm` base class extending :class:`~flask_wtf.FlaskForm` that adds support for specifying the rendered field order
- automatically set the `csrf_token` cookie on responses
- override the `click` module to also support documenting arguments with `help`
   - also make the default help options `-h` and `--help` instead of just `--help`
- refactor the hook store to be a class attribute of the bundle the hook(s) belong to
- add an `env` attribute on the `FlaskUnchained` app instance
- make the `bundles` attribute on the `Unchained` extension an `AttrDict`
   - bundles are now instantiated instead of passing the classes around directly
- add default config options, making `DEBUG` and `TESTING` unnecessary to set manually
- add a `_name` attribute to `FlaskForm` to automatically name forms when rendering them programmatically
- add `get_extension_local_proxy` and `get_service_local_proxy` methods to the `Unchained` extension
- add support for overriding static files from bundles
- minor refactor of the declarative routing for `Controller` and `Resource` classes
   - consolidate default route rule generation into the `Route` class
   - make it possible to override the `member_param` of a `Resource` with the `resource` routes function
- add a `TEMPLATE_FILE_EXTENSION` option to `AppConfig` that controllers will respect by default. Controllers can still set their `template_file_extension` attribute to override the application-wide default.
- implement missing `delete` routing function
- preliminary support for customizing the generated unique member param
- fix setting of `Route._controller_cls` to automatically always happen
- refactor the SQLAlchemy Bundle to split most of it out into its own package, so that it can be used on its own (without Flask).
- fix the resource url prefix descriptor to convert to kebab-case instead of snake-case
- rename `Controller.template_folder` to `Controller.template_folder_name`
- add `Controller.make_response` as an alias for `flask.make_response`
- convert attributes on `Controller`, `Resource`, and `ModelResource` to be `class Meta` options
- rename `_meta` to `Meta` per py-meta-utils v0.3
- rename `ModelManager.find_all` to `ModelManager.all` and `ModelManager.find_by` to `ModelManager.filter_by` for consistency with the `Query` api
- move instantiation of the `CSRFProtect` extension from the security bundle into the controller bundle, where it belongs, so that it always gets used
- improve registration of request cycle functions meant to run only for a specific bundle blueprint
- update `BaseService` to use a MetaOptionsFactory
- make the `ModelManager.model` class attribute a meta option
- rename the `flask db drop --drop` option to `flask db drop --force` to skip prompting
- rename the `flask db reset --reset` option to `flask db reset --force` to skip prompting
- add `no_autoflush` to `SessionManager`

## v0.5.1 (2018/07/25)

- include html templates in the distribution
- add bundles to the shell context

## v0.5.0 (2018/07/25)

- export `FlaskUnchained` from the root package
- export Flask's `current_app` from the root package
- never register static assets routes with babel bundle
- integrate the admin bundle into the `flask_unchained` package
- integrate the api bundle into the `flask_unchained` package
- integrate the celery bundle into the `flask_unchained` package
- integrate the mail bundle into the `flask_unchained` package
- integrate the sqlalchemy bundle into the `flask_unchained` package
- integrate the webpack bundle into the `flask_unchained` package

## v0.4.2 (2018/07/21)

- fix tests when babel_bundle isn't loaded

## v0.4.1 (2018/07/20)

- fix infinite recursion error when registering urls and blueprints with babel

## v0.4.0 (2018/07/20)

- make `tests._unchained_config` optional if `unchained_config` exists
- fix discovery of bundle views to include any bundle in the hierarchy with views
- subclass Flask to improve handling of adding blueprints and url rules in conjunction with the babel bundle
- rename `unchained.BUNDLES` to `unchained.bundles`

## v0.3.2 (2018/07/16)

- fix naming of bundle static endpoints

## v0.3.1 (2018/07/16)

- support loading bundles as the app bundle for development
- refactor the babel commands to work with both app and regular bundles
- fix discovery of tests._unchained_config module

## v0.3.0 (2018/07/14)

- add `flask qtconsole` command
- rename Bundle.iter_bundles to Bundle.iter_class_hierarchy
- add `cli_runner` pytest fixture for testing click commands
- fix register commands hook to support overriding groups and commands
- support registering request hooks, template tags/filters/tests, and context processors via deferred decorators on the Unchained and Bundle classes
- ship the controller bundle, session bundle, and babel bundles as part of core
   - the babel and controller bundles are now mandatory, and will be included automatically

## v0.2.2 (2018/04/08)

- bugfix: Bundle.static_url_prefix renamed to Bundle.static_url_path

## v0.2.1 (2018/04/08)

- bugfix: check for `FunctionType` in `set_up_class_dependency_injection`

## v0.2.0 (2018/04/06)

- rename `BaseConfig` to `Config`
- add utilities for dealing with optional dependencies:
   - `OptionalClass`: generic base class that can also be used as a substitute for extensions that have base classes defined as attributes on them
   - `optional_pytest_fixture`: allows to conditionally register test fixtures
- hooks now declare their dependencies by hook name, as opposed to using an integer priority

## v0.1.x

- early releases
