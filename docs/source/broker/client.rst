Client
======

With the client it is possible to work with the broker during the command line.
You can run it by simple execute ``python3 client.py --help``.

.. tip::

    If you run on docker use ``docker exec -it <container_name> python3 client.py --help``.

The following parameters are available:

* ``-h`` or ``--help``: Show the help message.
* ``broker``: Submenu for broker commands.
* ``skills``: Submenu for skill commands.

Broker
------

The broker submenu contains the following commands:

* ``-h`` or ``--help``: Show the help message.
* ``scrub``: Start :doc:`scrub <db.rst>` job for the database.
* ``init``: Set the current system admins' public key.
* ``assign``: Assign a role to a user (with the user's public key).


Skills
------

The skill submenu contains the following commands:

* ``-h`` or ``--help``: Show the help message.
* ``list``: List all available skills.
