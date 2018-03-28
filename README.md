# Flask Unchained

## The better way to build large Flask applications.

Flask Unchained is an extension that implements the Application Factory Pattern. It provides a standardized (by convention) way to organize "bundles" of code, such that they become easily distributable, reusable, and customizable across multiple Flask projects (similar to Django's "apps", with an architecture heavily inspired by Symfony). The ultimate goal is to provide a complete optional-batteries-included web application framework experience built on top of Flask.

* [**Flask Controller Bundle**](https://github.com/briancappello/flask-controller-bundle)
    - auto-discovers blueprints, controllers, and views across bundles
    - support for declarative routing (similar to Django's `urls.py`)
    - (think of it as the best ideas from Flask-RESTful, Flask-Classful, Flask's MethodView, and Flask-Via - all combined into one coherent solution)

* [**Flask API Bundle**](https://github.com/briancappello/flask-api-bundle)
    - extends Flask Controller Bundle with support for ModelResource controllers integrated with Marshmallow and SQLAlchemy

* [**Flask Webpack Bundle**](https://github.com/briancappello/flask-webpack-bundle) (integrates Webpack)

* [**Flask SQLAlchemy Bundle**](https://github.com/briancappello/flask-sqlalchemy-bundle) (integrates Flask-SQLAlchemy and Flask-Migrate)
    - auto-discovers models across bundles

* [**Flask Security Bundle**](https://github.com/briancappello/flask-security-bundle) (integrates Flask-Security)

* [**Flask Session Bundle**](https://github.com/briancappello/flask-session-bundle) (integrates Flask-Session)

* [**Flask Mail Bundle**](https://github.com/briancappello/flask-mail-bundle) (integrates Flask-Mail)

* [**Flask Celery Bundle**](https://github.com/briancappello/flask-celery-bundle) (integrates Celery)
    - auto-discovers tasks across bundles
