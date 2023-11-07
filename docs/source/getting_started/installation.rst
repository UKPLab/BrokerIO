.. _installation:
Installation
============
This section describes how to install the Broker.

Prerequisites
*************

Docker and docker-compose are required to run the NLP server.
Please install them according to the official documentation:

* `Docker <https://docs.docker.com/engine/installation/>`_
* `Docker Compose <https://docs.docker.com/compose/install/>`_


Build
*****

To build the NLP server, run the following command in the root directory of the project:

.. code-block:: bash

    make ENV=main build

This will build all docker image for the NLP server.

.. warning::::

    The ``ENV`` variable must be set to ``main`` or ``dev``, otherwise connection to the DB is not possible!
    The ``dev`` environment is used for development purpose only.
