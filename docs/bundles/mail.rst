Mail Bundle
-----------

Integrates `Flask Mail <https://pythonhosted.org/flask-mail/>`_ with Flask Unchained.

Dependencies
^^^^^^^^^^^^

* Flask Mail
* BeautifulSoup4
* lxml

Installation
^^^^^^^^^^^^

Install dependencies:

.. code:: bash

   $ pip install flask-unchained[mail]

And enable the bundle in your ``unchained_config.py``:

.. code:: python

   # your_project_root/unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.mail',
   ]

Config
^^^^^^

.. automodule:: flask_unchained.bundles.mail.config
   :members:

Commands
^^^^^^^^

.. click:: flask_unchained.bundles.mail.commands:mail
   :prog: flask mail
   :show-nested:

API Documentation
^^^^^^^^^^^^^^^^^

.. automodule:: flask_unchained.bundles.mail
   :members:

Extensions
~~~~~~~~~~

.. automodule:: flask_unchained.bundles.mail.extensions
   :members:

Utils
~~~~~

.. automodule:: flask_unchained.bundles.mail.utils
   :members:

