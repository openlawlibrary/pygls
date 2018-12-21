.. _testing:

Testing
=======

Unit Tests
----------

Writing unit tests for registered features and commands are easy and you don't
have to mock the whole language server. If you skipped the advanced usage page,
take a look at :ref:`passing language server instance <passing-instance>`
section for more details.

Json Extension example's `unit tests`_ might be helpful, too.

Integration Tests
-----------------

Integration tests coverage includes the whole workflow, from sending the client
request, to getting the result from the server. Since the *Language Server
Protocol* defines bidirectional communication between the client and the
server, we used *pygls* to simulate the client and send desired requests to the
server. To get better understanding of how setup it, take a look at our test
`fixtures`_.


.. _unit tests: https://github.com/openlawlibrary/pygls/blob/master/examples/json-extension/server/tests/unit
.. _fixtures: https://github.com/openlawlibrary/pygls/blob/master/tests/conftest.py#L29
