# CHANGELOG

## 0.6.0 (unreleased)

* export `get_boolean_env` from core `flask_unchained` package
* export `param_converter` from core `flask_unchained` package
* fix discovery of user-app `tests._unchained_config`
* improve the output of commands that display their information in a table
* improve the output of custom sqlalchemy types in generated migrations files
* improve the output of the Views column from the `flask urls` command
* improve the `--order-by` option of the `flask urls` command
* rename command `flask db import_fixtures` to `flask db import-fixtures`
* add a `FlaskForm` base class extending :class:`~flask_wtf.FlaskForm` that adds support for specifying the rendered field order
* automatically set the `csrf_token` cookie on responses
* override the `click` module to also support documenting arguments with `help`
 - also make the default help options `-h` and `--help` instead of just `--help`
* refactor the hook store to be a class attribute of the bundle the hook(s) belong to
* add an `env` attribute on the `FlaskUnchained` app instance
* make the `bundles` attribute on the `Unchained` extension an `AttrDict`
   - bundles are now instantiated instead of passing the classes around directly
* add default config options, making `DEBUG` and `TESTING` unnecessary to set manually
* add a `_form_name` attribute to `FlaskForm` to automatically name forms when rendering them programmatically
* add `get_extension_local_proxy` and `get_service_local_proxy` methods to the `Unchained` extension
* add support for overriding static files from bundles
* minor refactor of the declarative routing for `Controller` and `Resource` classes
   - consolidate default route rule generation into the `Route` class
   - make it possible to override the `member_param` of a `Resource` with the `resource` routes function
* add a `TEMPLATE_FILE_EXTENSION` option to `AppConfig` that controllers will respect by default. Controllers can still set their `template_file_extension` attribute to override the application-wide default.
* implement missing `delete` routing function
* preliminary support for customizing the generated unique member param

## 0.5.1 (2018/07/25)

* include html templates in the distribution
* add bundles to the shell context

## 0.5.0 (2018/07/25)

* export `FlaskUnchained` from the root package
* export Flask's `current_app` from the root package
* never register static assets routes with babel bundle
* integrate the admin bundle into the `flask_unchained` package
* integrate the api bundle into the `flask_unchained` package
* integrate the celery bundle into the `flask_unchained` package
* integrate the mail bundle into the `flask_unchained` package
* integrate the sqlalchemy bundle into the `flask_unchained` package
* integrate the webpack bundle into the `flask_unchained` package

## 0.4.2 (2018/07/21)

* fix tests when babel_bundle isn't loaded

## 0.4.1 (2018/07/20)

* fix infinite recursion error when registering urls and blueprints with babel

## 0.4.0 (2018/07/20)

* make `tests._unchained_config` optional if `unchained_config` exists
* fix discovery of bundle views to include any bundle in the hierarchy with views
* subclass Flask to improve handling of adding blueprints and url rules in conjunction with the babel bundle
* rename `unchained.BUNDLES` to `unchained.bundles`

## 0.3.2 (2018/07/16)

* fix naming of bundle static endpoints

## 0.3.1 (2018/07/16)

* support loading bundles as the app bundle for development
* refactor the babel commands to work with both app and regular bundles
* fix discovery of tests._unchained_config module

## 0.3.0 (2018/07/14)

* add `flask qtconsole` command
* rename Bundle.iter_bundles to Bundle.iter_class_hierarchy
* add `cli_runner` pytest fixture for testing click commands
* fix register commands hook to support overriding groups and commands
* support registering request hooks, template tags/filters/tests, and context processors via deferred decorators on the Unchained and Bundle classes
* ship the controller bundle, session bundle, and babel bundles as part of core
    - the babel and controller bundles are now mandatory, and will be included automatically

## 0.2.2 (2018/04/08)

* bugfix: Bundle.static_url_prefix renamed to Bundle.static_url_path

## 0.2.1 (2018/04/08)

* bugfix: check for `FunctionType` in `set_up_class_dependency_injection`

## 0.2.0 (2018/04/06)

* rename `BaseConfig` to `Config`
* add utilities for dealing with optional dependencies:
    * `OptionalClass`: generic base class that can also be used as a substitute for extensions that have base classes defined as attributes on them
    * `optional_pytest_fixture`: allows to conditionally register test fixtures
* hooks now declare their dependencies by hook name, as opposed to using an integer priority

## 0.1.x

* early releases
