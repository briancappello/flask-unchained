config files
------------

It would be better to have a standard location for an unchained config.

`PROJECT_ROOT/config/unchained.py` perhaps? it should look like this:

APP_NAME = 'whatever'             # first argument to Flask constructor
TEMPLATE_FOLDER = 'templates'     # kwarg to Flask constructor
STATIC_FOLDER = 'public'          # kwarg to Flask constructor
STATIC_URL_PATH = '/static'       # kwarg to Flask constructor
BUNDLES = []

would be much more clear in terms of configuring the app bundle
> global Flask settings are in a global config
> configure app-bundle-specific template_folder, static_folder, and
  static_url_path on the AppBundle class (like every other bundle) instead
  of in the app bundle's config (unlike every other bundle; confusing)

would also remove the need for FLASK_APP_BUNDLE environment variable

* rename BaseConfig to Config

* document how defaults, inheritance and overriding works


documentation - JFDI
-------------

* motivation / why i think it's awesome / benefits
* conventions, how bundles work and how unchained boots up end user apps


tests
-----

* di subsystem, register services hook needs tests
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

maybe?
------
- would be better for hooks to declare dependencies by name, instead of priority numbers
    > does it make sense to combine the hook resolution order with that of extensions?
        - most likely YAGNI, and it would be a somewhat big change for... what gain exactly?
