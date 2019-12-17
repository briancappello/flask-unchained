api bundle
----------
* finish integrating OpenAPI/APISpec
* add support for ETags
* probably room for many more improvements, it's a big domain...


sqlalchemy bundle
-----------------
* create test database if it doesn't exist (see `db` fixture in `bundles/sqlalchemy/pytest.py`)

security bundle
---------------
* implement GraphQL support (integrate with Graphene Bundle)
* implement support for JWT tokens (and maybe PASETO tokens too?)


oauth bundle
------------
* switch over from deprecated Flask-OAuthlib to [authlib](https://github.com/lepture/authlib)


mail bundle
-----------
* add extensible/pluggable support for API-based mail providers, eg SendGrid, MailGun, ...


dotenv files
------------
* [flask-dotenv](https://github.com/grauwoelfchen/flask-dotenv/) perhaps?


logging
-------
* integrate Flask-LogConfig (or Loguru, rather new but looks promising)


documentation
-------------
* improve documentation, use cases, and examples for all the bundles
* document creating extendable bundles
* finish tutorial


dependency injection
--------------------
* make dependency injection of optional extensions/services work everywhere (currently it only works on the constructor of services)
* should services be lazily instantiated on an as-needed basis?
* maybe make the `injectable` default parameter value optional if the type annotation is recognized as a registered service or extension?


better webpack support
----------------------
* a solution to support distributing assets with bundles would be really nice
* maybe also default configs for common setups?
   - hot reloading would be nice
   - or perhaps integration with common tools, eg create react app


admin bundle
------------
* admin bundle could also use some improvement
   - honestly i haven't spent much time looking too deeply into flask-admin, and am kind of leaning towards investigating building something around React-Admin


bucket list
-----------
* websockets support (probably the best bet would be to investigate compatibility with [Quart](https://gitlab.com/pgjones/quart))
* out-of-the-box support for production deployment
   - Docker
   - Ansible
   - AWS
   - GCP
* frontend app templates
   - React (perhaps [react-boilerplate](https://github.com/react-boilerplate/react-boilerplate)?)
   - Angular
   - Vue
