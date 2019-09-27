api bundle
----------
* finish integrating OpenAPI/APISpec
* add support for `Accept` headers (ie supporting response types other than json)
* add support for ETags
* probably room for many more improvements, it's a big domain...


security bundle
---------------
* implement GraphQL support
* implement support for JWT tokens (and maybe PASETO tokens too?)


oauth bundle
------------
* switch over from deprecated Flask-OAuthlib to https://github.com/lepture/authlib


mail bundle
-----------
* add extensible/pluggable support for API-based mail providers, eg SendGrid, MailGun, ...


logging
-------
* integrate Flask-LogConfig (or Loguru, rather new but looks promising)


documentation
-------------
* improve documentation/use cases/examples for all the bundles
* document creating extendable bundles
* finish tutorial


dependency injection
--------------------
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
   - React
   - Angular
   - Vue
