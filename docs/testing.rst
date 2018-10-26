Testing with pytest
===================

Included pytest fixtures
------------------------

app
^^^

.. autofunction:: flask_unchained.pytest.app

maybe_inject_extensions_and_services
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: flask_unchained.pytest.maybe_inject_extensions_and_services

cli_runner
^^^^^^^^^^

.. autofunction:: flask_unchained.pytest.cli_runner

client
^^^^^^

.. autofunction:: flask_unchained.pytest.client

.. autoclass:: flask_unchained.pytest.HtmlTestResponse
   :members:

api_client
^^^^^^^^^^

.. autofunction:: flask_unchained.pytest.api_client

templates
^^^^^^^^^

.. autofunction:: flask_unchained.pytest.templates

Testing related classes
-----------------------

FlaskCliRunner
^^^^^^^^^^^^^^

.. autoclass:: flask_unchained.pytest.FlaskCliRunner
   :members:

HtmlTestClient
^^^^^^^^^^^^^^

.. autoclass:: flask_unchained.pytest.HtmlTestClient
   :members:

HtmlTestResponse
^^^^^^^^^^^^^^^^

.. autofunction:: flask_unchained.pytest.api_client

ApiTestClient
^^^^^^^^^^^^^

.. autoclass:: flask_unchained.pytest.ApiTestClient
   :members:

ApiTestResponse
^^^^^^^^^^^^^^^

.. autoclass:: flask_unchained.pytest.ApiTestResponse
   :members:

RenderedTemplate
^^^^^^^^^^^^^^^^

.. autoclass:: flask_unchained.pytest.RenderedTemplate
   :members:
