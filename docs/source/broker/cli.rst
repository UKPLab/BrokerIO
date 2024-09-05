Command Line Interface
======================

With the client it is possible to work with the broker during the command line.
Manually install it with `pip install .` in the root directory of the project.
You can run it by simple execute ``brokerio --help``.

.. tip::

    For development, you can also use the command line interface with the python module directly ``python3 -m brokerio --help``.
    Therefore, you need to install the conda environment, see :doc:`Development </broker/development>`


.. tip::

    # TODO add docker instructions
    If you run on docker use ``docker exec -it <container_name> python3 -m brokerio --help``.

The following parameters are available:

* ``-h`` or ``--help``: Show the help message.
* ``broker``: Submenu for broker commands.
* ``guard``: Submenu for guard commands.
* ``skills``: Submenu for skill commands.

Broker CLI
----------

This will be in the future the main interface for the broker.
Currently is is possible to use it with ``python3 -m brokerio broker --help``.

* ``-h`` or ``--help``: Show the help message.
* ``scrub``: Start :doc:`scrub <db>` job for the database.
* ``init``: Set the current system admins' public key.
* ``assign``: Assign a role to a user (with the user's public key).


Skills CLI
----------

With the skills submenu you can publish several integrated models to the broker (see :doc:`available models </models/models>` for a list).
The following commands are available:

* ``-h`` or ``--help``: Show the help message.
* ``list``: List all available skills.
* ``build``: Build the container for the skills
* ``run``: Run the container for the skills
* ``stop``: Stop the container for the skills

.. tip::

    There are many extra parameter available, use ``-h`` to see all available parameters for each command.