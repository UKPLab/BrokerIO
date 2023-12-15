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
* ``scrub``: Start :doc:`scrub <db>` job for the database.
* ``init``: Set the current system admins' public key.
* ``assign``: Assign a role to a user (with the user's public key).


Skills
------

With the skills submenu you can publish several integrated models to the broker (see :doc:`available models </models/models>` for a list). The following commands are available:

* ``-h`` or ``--help``: Show the help message.
* ``list``: List all available skills.
* ``build``: Build the container for the skills
* ``run``: Run the container for the skills
* ``stop``: Stop the container for the skills

.. tip::

    Always use ``-h`` to see all available parameters for the commands.