Development
===========

If you want to contribute to the development of the project, please follow the steps below.

Prerequisites
*************

In addition to the packages listed in :doc:`installation <./installation>`, you will need install conda:

* `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_

Run
***

The following commands will create a new conda environment and install all required packages:

.. code-block:: shell

    conda env create -f environment.yaml
    conda activate nlp_api
    conda env update --file environment.yaml --name nlp_api --prune # update environment

To have a fully running development setup run each command in different terminal:

.. code-block:: shell

    make docker
    make run

.. note::

    You can also build the environment locally, but the connection to redis might be broken.
    Use `make ENV=dev build` to get a running local environment.

Test
****

To test the broker, there are several unit tests available.
To run them, execute the following command:

.. code-block:: shell

    make test

The test are located in the ``tests`` folder.

.. tip::

    You also can run the tests individually by using, e.g. ``python3 -u -m unittest test.test_broker.TestBroker.test_auth``.

Error Codes
===========

Sometimes the broker will return an error code, here is a list of all possible error codes:

- 100 - Request Quota exceeded
- 101 - Job Quota exceeded
- 102 - Job cancelled - maximum execution time exceeded
- 103 - Lost connection to node - and no other node available
- 104 - Lost connection to node - job is started on another node
- 200 - Skill not available
- 401 - Signature cannot be verified by message
- 500 - Undefined error in request

Debugging
*********

To debug the redis server, you can use the redis-cli:

.. code-block:: shell

    sudo apt-get install redis-tools
    redis-cli --stat
    redis-cli --scan | head -10

Frameworks
**********

The following frameworks are used inside the broker:

- https://docs.python-arango.com/
- https://www.pycryptodome.org/

