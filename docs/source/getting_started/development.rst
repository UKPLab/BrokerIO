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

Test
****

To test if the server is available and running, run the following command:

.. code-block:: shell

    cd broker
    python test.py --url "http://127.0.0.1:4853" --token "<see .env file>"

Debugging
*********

To debug the redis server, you can use the redis-cli:

.. code-block:: shell

    sudo apt-get install redis-tools
    redis-cli --stat
    redis-cli --scan | head -10

