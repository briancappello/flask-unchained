config files
------------
* need a good way for bundle configs to get access to the current app config during initialization (probably somehow need to LocalProxy to it... challenge is app ctx)
* probably would be nice to have some kind of command to view the current config
    - maybe filter by bundle


api bundle
----------
* finish integrating OpenAPI/APISpec


security bundle
---------------
* implement support for JWT tokens (and maybe PASETO tokens too?)


logging
-------
* integrate Flask-LogConfig (or Logbook, need to investigate)


documentation
-------------
* conventions, how bundles work and how unchained boots up end user apps
* document usage of all the bundles
* document creating extendable bundles, how to integrate stock Flask extensions
* finish tutorial


tests
-----
* add more tests for the di subsystem, eg register services hook needs tests
* register commands hook


lower priority
--------------
* verify it's possible to override hooks (certainly bundles should be able to override hooks from parent bundles, but should it also be possible to override unchained's hooks too?)
* webpack support could use some improvement
   - maybe default configs for common setups?
   - hot reloading would be nice


bucket list
-----------
* out-of-the-box support for production deployment
   - docker
   - AWS
   - GCP
   - ansible? it works but it's got some pain points
* frontend app templates
   - react
   - angular
   - vue
