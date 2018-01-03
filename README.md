# Flask Unchained

## The better way to build large Flask applications.

Flask Unchained is an extension that implements the Application Factory Pattern. It provides a standardized way to organize "bundles" of code, such that they become easily distributable and reusable across multiple Flask projects (similar to Django's "apps"). This project adds support for auto-discovering other Flask extensions and click commands/groups from bundles. These are some of the other bundles which can be combined to provide a complete web application framework experience with Flask:

* [**Flask Controller Bundle**](https://github.com/briancappello/flask-controller-bundle)
    - auto-discovers blueprints, controllers, and views across bundles
    - support for declarative routing (similar to Django's `urls.py`)
    - (think of it as the best ideas from Flask-RESTful, Flask-Classful, Flask's MethodView, and Flask-Via - combined into one coherent solution)

* [**Flask API Bundle**](https://github.com/briancappello/flask-api-bundle)
    - extends Flask Controller Bundle with support for Marshmallow serializers and Swagger API Docs

* [**Flask Webpack Bundle**](https://github.com/briancappello/flask-webpack-bundle) (integrates Flask-Webpack)

* [**Flask SQLAlchemy Bundle**](https://github.com/briancappello/flask-sqlalchemy-bundle) (integrates Flask-SQLAlchemy and Alembic migrations)
    - auto-discovers models across bundles

* [**Flask Fixtures Bundle**](https://github.com/briancappello/flask-fixtures-bundle) (populate SQLAlchemy models from Jinja-YAML files)

* [**Flask Security Bundle**](https://github.com/briancappello/flask-security-bundle) (integrates Flask-Security)

* [**Flask Session Bundle**](https://github.com/briancappello/flask-session-bundle) (integrates Flask-Session)

* [**Flask Mail Bundle**](https://github.com/briancappello/flask-mail-bundle) (integrates Flask-Mail)

* [**Flask Celery Bundle**](https://github.com/briancappello/flask-celery-bundle) (integrates Celery)
    - auto-discovers tasks across bundles
