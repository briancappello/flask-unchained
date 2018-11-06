Mail Bundle
-----------

Integrates `Flask Mail <https://pythonhosted.org/flask-mail/>`_ with Flask Unchained.

Installation
^^^^^^^^^^^^

Install dependencies:

.. code:: bash

   pip install flask-unchained[mail]

And enable the bundle in your ``unchained_config.py``:

.. code:: python

   # your_project_root/unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.mail',
       'app',
   ]

NOTE: If you have enabled the :doc:`celery`, and want to send emails asynchronously using Celery, then you must list the celery bundle *after* the mail bundle in ``BUNDLES``.

Config
^^^^^^

.. automodule:: flask_unchained.bundles.mail.config
   :members:
   :noindex:

Usage
^^^^^

After configuring the bundle, usage is simple::

   from flask_unchained.bundles.mail import mail

   mail.send_message('hello world', to='foo@bar.com')

``mail`` is an instance of the :class:`~flask_unchained.bundles.mail.Mail` extension, and :meth:`~flask_unchained.bundles.mail.Mail.send_message` is the only public method on it. Technically, it's an alias for :meth:`~flask_unchained.bundles.mail.Mail.send`, which you can also use. (The :meth:`~flask_unchained.bundles.mail.Mail.send` method is maintained for backwards compatibility with the stock Flask Mail extension, although it has a different but compatible function signature than the original - we don't require that you manually create :class:`~flask_mail.Message` instances yourself before calling :meth:`~flask_unchained.bundles.mail.Mail.send`.)

Commands
^^^^^^^^

.. click:: flask_unchained.bundles.mail.commands:mail
   :prog: flask mail
   :show-nested:

pytest fixtures
^^^^^^^^^^^^^^^

The mail bundle includes one pytest fixture, :func:`~flask_unchained.bundles.mail.pytest.outbox`, that you can use to verify that emails were sent::

   def test_something(client, outbox):
       r = client.get('endpoint.that.sends.an.email')
       assert len(outbox) == 1
       assert outbox[0].subject == 'hello world'
       assert 'hello world' in outbox[0].html

API Documentation
^^^^^^^^^^^^^^^^^

See :doc:`../api/mail_bundle`
