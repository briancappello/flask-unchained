config files
------------
* need a good way for bundle configs to get access to the current app config during initialization (probably somehow need to LocalProxy to it... challenge is app ctx)
* probably would be nice to have some kind of command to view the current config
    - maybe filter by bundle


api bundle
----------
* finish integrating OpenAPI/APISpec


logging
-------
* integrate Flask-LogConfig (or Logbook, need to investigate)


documentation - JFDI
--------------------
* conventions, how bundles work and how unchained boots up end user apps
* document usage of all the bundles


tests
-----
* add more tests for the di subsystem, eg register services hook needs tests
* register commands hook


lower priority
--------------
* verify it's possible to override hooks (certainly bundles should be able to override hooks from parent bundles, but should it also be possible to override unchained's hooks too?)
