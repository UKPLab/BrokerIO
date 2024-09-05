Quickstart Guide
=================

This guide will help you get started with the Broker.

| You can either install the BrokerIO on your local machine via a pip or use the Broker as a service in Docker.
| For a complete installation, please follow the instructions in :doc:`Installation <./installation>`.

Quick and dirty
---------------

To install the BrokerIO on your local machine, you can use the following command in the root directory of the repository:

.. code-block:: bash

    pip install .
    brokerio broker init
    brokerio broker start

for a Docker installation, you can use the following command:

.. code-block:: bash

    make docker

BrokerIO is available under `http://localhost:4852` now.

Sequence Diagram
----------------

To give you a better understanding of the communication between the **Broker**, **Skills** and **Clients**, we provide a sequence diagram of the communication.
**Skills** are the models, features or tools that are provided by the **Broker** and that can be executed by the **Clients**.

.. image:: ./sequence.drawio.svg
   :width: 80%
   :align: center

Usage
-----

To use the broker you can use any Socket.IO API:

- `Socket.IO Client Libraries for Javascript <https://socket.io/docs>`_
- `Socket.IO Client Libraries for Python <https://python-socketio.readthedocs.io/en/latest/>`_

Here we provide some basic example for the Javascript API:

.. code-block:: javascript

    const {io} = require("socket.io-client");
    const socket = io("<broker url>", {
        query: {token: "<see .env file>"},
        reconnection: true,
        autoConnect: true,
        timeout: 10000, //timeout between connection attempts
    });

    socket.on('connect', function() {
        console.log('Connected to NLP Broker');
        socket.emit('skillGetAll')
    });

    // Received skill updates from the broker
    socket.on('skillUpdate', function(data) {
        console.log("New skill updates: " + data);
        // get config of first skill
        socket.emit('skillGetConfig', {name: data[0]['name']});
    });

    // Receive skill config from the broker
    socket.on('skillConfig', function(data) {
        console.log("Skill config for {}: {}".format(data['name'], data));
    });

    socket.on('disconnect', function() {
        console.log('disconnected');
    });

.. role:: javascript(code)
   :language: javascript

To execute a skill just call:

.. code-block:: javascript

    socket.emit("skillRequest", {id: "<unique id>", name: "<skill name>", data: "<skill data>", config: {donate: true}});


.. note::

    For authentication see :doc:`Authentication <../broker/authentication>`.

.. tip::

    Further examples (jupyter notebooks) can be found in the ``examples`` folder.