
# Flask Unchained

## The better way to build large Flask applications.

Flask Unchained is an extension that implements the Application Factory Pattern. It provides a standardized (by convention) way to organize "bundles" of code, such that they become easily distributable, reusable, and customizable across multiple independent Flask Unchained projects (similar to Django's "apps", with an architecture inspired by [Symfony](https://symfony.com/). The ultimate goal is to provide an integrated, optional-batteries-included web application framework built on top of Flask.

Currently Flask Unchained includes the following bundles:

* **Admin Bundle**
   - integrates [Flask-Admin](https://flask-admin.readthedocs.io/en/latest/)

* **API Bundle**
    - extends the Controller Bundle with support for ModelResource controllers integrated with SQLAlchemy and Marshmallow
    - includes optional support generating API docs via APISpec/OpenAPI (using ReDoc as the frontend)

* **Babel Bundle**
   - integrates support for translations via [Flask-BabelEx](https://pythonhosted.org/Flask-BabelEx/)

* **Celery Bundle**
   - integrates [Celery](http://www.celeryproject.org/)
   - auto-discovers tasks across bundles

* **Controller Bundle**
    - auto-discovers blueprints, controllers, and views across bundles
    - support for declarative routing (similar to Django's `urls.py`)
    - (think of it as the best ideas from Flask-RESTful, Flask-Classful, Flask's MethodView, and Flask-Via - all combined into one coherent solution)

* **Mail Bundle**
   - integrates [Flask-Mail](https://pythonhosted.org/flask-mail/)

* **Security Bundle**
   - integrates a heavily cleaned up [Flask-Security](https://pythonhosted.org/Flask-Security/index.html) (just about everything except for the core session and encryption logic has been rewritten for your sanity)

* **Session Bundle**
   - integrates support for server-side sessions via [Flask-Session](https://pythonhosted.org/Flask-Session/)

* **SQLAlchemy Bundle**
   - integrates Flask-SQLAlchemy and Flask-Migrate
   - auto-discovers models across bundles
   - adds support for performing validation on models (including integration with Flask-WTF and Marshmallow, so that validation rules can be as DRY as possible)

* **Webpack Bundle**
   - integrates Webpack
