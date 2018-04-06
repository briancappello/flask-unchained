config files
------------

* document how defaults, inheritance and overriding works


logging
-------
integrate Flask-LogConfig (or Logbook, need to investigate)


documentation - JFDI
-------------

* motivation / why i think it's awesome / benefits
* conventions, how bundles work and how unchained boots up end user apps


tests
-----

* add more tests for the di subsystem, eg register services hook needs tests
* register commands hook

lower priority:
- verify it's possible to override hooks (certainly bundles should be able to override hooks from parent bundles, but should it also be possible to override unchained's hooks too?)


flask controller bundle: should probably make this core, like DI
----------------------------------------------------------------
- figure out the automatic behind-the-scenes blueprints shit
    > all registered routes from a bundle hierarchy should be in one blueprint
        - allows for bp-specific context processors, request hooks, etc
    > separate template-specific blueprints for each bundle in the hierarchy
        - decoupled from views/controllers
        - allows for loading and extending templates
