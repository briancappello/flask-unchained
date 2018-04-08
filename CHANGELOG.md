# CHANGELOG

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
