api bundle [help wanted]
------------------------
* finish integrating OpenAPI/APISpec
* add support for `Accept` headers (ie supporting response types other than json)
* add support for ETags
* probably room for many more improvements, it's a big domain...


security bundle [help wanted]
-----------------------------
* implement support for JWT tokens (and maybe PASETO tokens too?)


oauth bundle
------------
* switch over from deprecated Flask-OAuthlib to https://github.com/lepture/authlib


logging
-------
* integrate Flask-LogConfig (or Loguru, rather new but looks promising)


documentation
-------------
* document usage of admin, babel, and webpack bundles
* document creating extendable bundles
* finish tutorial


dependency injection
--------------------
* should services be lazily instantiated on an as-needed basis?
* maybe make the `injectable` default parameter value optional if the type annotation is recognized as a registered service or extension?


webpack support [help wanted]
-----------------------------
* a solution to support distributing assets with bundles would be really nice
* maybe also default configs for common setups?
   - hot reloading would be nice
   - or perhaps integration with common tools, eg create react app


lower priority
--------------
* admin bundle could also use some improvement
   - honestly i haven't spent much time looking too deeply into flask-admin, and am kind of leaning towards investigating building something around React-Admin
* it should probably be possible to define multiple modules a hook should load from


bucket list [help wanted]
-------------------------
* websockets support (probably the best bet would be to investigate compatibility with Quart)
* out-of-the-box support for production deployment
   - docker
   - AWS
   - GCP
   - ansible? it works but it's got some pain points
* frontend app templates
   - react
   - angular
   - vue
