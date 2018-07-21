# CHANGELOG

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

* bugfix: check for `FunctionType` in `setup_class_dependency_injection`

## 0.2.0 (2018/04/06)

* rename `BaseConfig` to `Config`
* add utilities for dealing with optional dependencies:
    * `OptionalClass`: generic base class that can also be used as a substitute for extensions that have base classes defined as attributes on them
    * `optional_pytest_fixture`: allows to conditionally register test fixtures
* hooks now declare their dependencies by hook name, as opposed to using an integer priority

## 0.1.x

* early releases
