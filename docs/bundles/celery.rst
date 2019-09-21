Celery Bundle
-------------

Integrates `Celery <http://www.celeryproject.org/>`_ with Flask Unchained.

Dependencies
^^^^^^^^^^^^

* A `broker <http://docs.celeryproject.org/en/latest/getting-started/brokers/index.html>`_ of some sort; Redis or RabbitMQ are popular choices.

Installation
^^^^^^^^^^^^

Install dependencies:

.. code:: bash

   pip install "flask-unchained[celery]" <broker-of-choice>

And enable the bundle in your ``unchained_config.py``:

.. code:: python

   # your_project_root/unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.celery',
       'app',
   ]

NOTE: If you have enabled the :doc:`mail`, and want to send emails asynchronously using celery, then you must list the celery bundle *after* the mail bundle in ``BUNDLES``.

Config
^^^^^^

.. autoclass:: flask_unchained.bundles.celery.config.Config
   :members:
   :noindex:

Commands
^^^^^^^^

.. click:: flask_unchained.bundles.celery.commands:celery
    :prog: flask celery
    :show-nested:

API Documentation
^^^^^^^^^^^^^^^^^

See :doc:`../api/celery_bundle`
