Welcome to the BrokerIO's documentation!
========================================

BrokerIO provide a simple interface to a variety of tools and models, so called **Skills**.
It is designed to be used by the BrokerIO API.
The API is based on websockets that reduces inference time when routing requests to the Skills.

With many additional features, the BrokerIO API is designed to be used by multiple clients at the same time,
distribute requests to the available Skills and provide easy access to the results.
A command line interface (CLI) easily allow to interact with the BrokerIO and to manage the available Skills.

The following features are supported:

- **Quota System**: Limit the number of requests a client can make
- **NoSQL Database**: Store the results of the Skills in a NoSQL database (inclusive donation feature)
- **Authentication**: Secure the access to the BrokerIO API via Role based access control (RBAC)
- **CLI**: Manage the BrokerIO and the available Skills via the command line
- **Logging**: Log all requests and responses to the BrokerIO API
- **Build-in Skills**: Provide a set of build-in Skills to get started
- **Docker Environment**: Run the BrokerIO in a Docker container

.. note::

   BrokerIO does not start any **Skills** by itself and if the models crash it is the responsibility of the models container
   to restart the model and reconnect to the Broker on their own.
   We also implemented a quota system to prevent a single client from using all available resources (see ::doc:`Config </broker/config>`).

| Tools and models are registered as so called :doc:`Skills <./skills/definition>`, each having a specific task.
| See :doc:`Quickstart <./getting_started/quickstart>` for a quick introduction to the Broker.

BrokerIO was developed as part of the `CARE project <https://github.com/UKPLab/CARE>`_ at the `UKP Lab <https://www.informatik.tu-darmstadt.de/ukp/ukp_home/index.en.jsp>`_ at the `TU Darmstadt <https://www.tu-darmstadt.de/index.en.jsp>`_.


.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   getting_started/quickstart
   getting_started/installation

.. toctree::
   :maxdepth: 1
   :caption: Broker

   broker/config
   broker/authentication
   broker/cli
   broker/requests
   broker/development
   broker/db



.. toctree::
   :maxdepth: 1
   :caption: Skills

   skills/definition
   skills/features
   skills/skill_definition_file
   skills/examples

.. toctree::
   :maxdepth: 1
   :caption: Models

   models/example
   models/models


