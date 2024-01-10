.. _testing:

Testing
=======

Unit Tests
----------

Writing unit tests for registered features and commands are easy and you don't
have to mock the whole language server. If you skipped the advanced usage page,
take a look at :ref:`passing language server instance <passing-instance>`
section for more details.

Integration Tests
-----------------

Integration tests coverage includes the whole workflow, from sending the client
request, to getting the result from the server. Since the *Language Server
Protocol* defines bidirectional communication between the client and the
server, we used *pygls* to simulate the client and send desired requests to the
server. To get a better understanding of how to set it up, take a look at our test
`fixtures`_.

.. _fixtures: https://github.com/openlawlibrary/pygls/blob/main/tests/conftest.py
