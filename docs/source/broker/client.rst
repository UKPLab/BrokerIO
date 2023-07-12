Client
======

With the client it is possible to work with the broker during the command line.
You can run it by simple execute ``python3 client.py <parameter>``.

.. tip::

    If you run on docker use ``docker exec -it <container_name> python3 client.py <parameter>``.

The following parameters are available:

* ``-h`` or ``--help``: Show the help message.
* ``--init True``: Set the current system admins' public key. (implicit in ``make init`` by create a new key pair)
* ``--scrub True``: Start :doc:`scrub <db.rst>` job for the database

You can also send a simple message to the broker by using the following parameters:

* ``--url <url>``: Set the url of the broker.
* ``--skill <skill>``: Set the skill of the message.