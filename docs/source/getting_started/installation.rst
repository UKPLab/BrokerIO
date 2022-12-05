.. _installation:
Installation
============

Our NLP Broker project is available on the UKP GitLab Repository:

https://git.ukp.informatik.tu-darmstadt.de/zyska/nlp_api

If you need access, please contact us under peer@ukp.tu-darmstadt.de.

Prerequisites
*************

Docker and docker-compose are required to run the NLP server.
Please install them according to the official documentation:

* `Docker <https://docs.docker.com/engine/installation/>`_
* `Docker Compose <https://docs.docker.com/compose/install/>`_

.. note::
    Make sure that your local installation of Celery is either compatible (see environment.yaml)
    or does not over-shadow the conda-installed version.

    Check location with `which celery` and version with `celery --version`.


Build
*****

To build the NLP server, run the following command in the root directory of the project:

.. code-block:: bash

    make build

This will build all docker image for the NLP server.