"""
DEV
~~~

.. data:: DEV

    Used to specify the development environment.

PROD
~~~~

.. data:: PROD

    Used to specify the production environment.

STAGING
~~~~~~~

.. data:: STAGING

    Used to specify the staging environment.

TEST
~~~~

.. data:: TEST

    Used to specify the test environment.
"""

DEV = 'development'
PROD = 'production'
STAGING = 'staging'
TEST = 'test'

_INJECT_CLS_ATTRS = '__inject_cls_attrs__'
_DI_AUTOMATICALLY_HANDLED = '__di_automatically_handled__'


__all__ = [
    'DEV',
    'PROD',
    'STAGING',
    'TEST',
]
