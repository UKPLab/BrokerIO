.. _installation:
Installation
============
This section describes how to install the BrokerIO.

Prerequisites
*************

Docker is required to build the Containers and Skills.
Please install them according to the official documentation:

* `Docker <https://docs.docker.com/engine/installation/>`_

or install Docker Desktop:

* `Docker Desktop for Windows <https://docs.docker.com/docker-for-windows/install/>`_
* `Docker Desktop for Mac <https://docs.docker.com/desktop/install/mac-install/>`_
* `Docker Desktop for Linux <https://docs.docker.com/desktop/install/linux-install/>`_

Also make sure that you have GNU's ``make`` installed on your system.

.. note::

    On Windows, you can use the ``make`` command with the `GNU Make for Windows <http://gnuwin32.sourceforge.net/packages/make.htm>`_ package.
    On newer windows systems, simply use ``winget install GnuWin32.Make`` and make it executable with ``set PATH=%PATH%;C:/Program Files (x86)/GnuWin32/bin``.

.. note::

    On Ubuntu, you need to install the docker compose plugin with ``sudo update && sudo apt-get install docker-compose-plugin``.


For installing the requirements of the command line interface see section :doc:`CLI </broker/client>`.

As a service
************

To build BrokerIO as a service, change the .env file to your requirements and
run the following command in the root directory of the project:

.. code-block:: bash

    make docker

This will build all relevant docker images to run BrokerIO (but without any Skills!).


Development
***********

To start the broker in development mode, run the following command in the root directory of the project:

.. code-block:: bash

    make db
    python3 -m brokerio broker start

See section :doc:`Development </broker/development>` for more information.



