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
