Quickstart Guide
=================

This guide will help you get started with the NLP Broker.

| You can either install the NLP Broker on your local machine or use the NLP Broker as a service.
| For a local installation, please follow the instructions in :doc:`Installation <./installation>`.
| If you want to use the NLP Broker as a service, you can connect the API through:

- |BROKER_WEBURL|

.. note::

    Please be aware that the NLP Broker is a websocket API based on `Socket.IO <https://socket.io/>`_ and therefore requires a websocket client to connect to it.
    The API is not accessible through a RESTful interface!

    | The full documentation of the API can be found under:
    | |BROKER_APIURL|

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
    });

    // Received skill updates from the broker
    // Note: When connecting to the broker, the broker will send
    // automatically all available skills to the client
    socket.on('skillUpdate', function(data) {
        console.log("New skill updates: " + data);
        // do something with the skills
    });

    socket.on('disconnect', function() {
        console.log('disconnected');
    });

.. role:: javascript(code)
   :language: javascript

To execute a skill just call:

:javascript:`socket.emit("skillRequest", {skill: "<skill name>", data: "<skill data>"});`
