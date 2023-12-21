Available models
================

The broker also provides some basic models that can be published as a skill.
The models can be published via the CLI client :doc:`CLI </broker/client>`.

.. tip::

    Always use the ``--help`` option to get an overview of the available options, as each model has different requirements.

OpenAI Azure
~~~~~~~~~~~~

This skill supports the OpenAI Azure API. For more details follow `Quickstart <https://learn.microsoft.com/en-us/azure/ai-services/openai>`_.

Example to run the skill:

.. code-block:: bash

    python3 client.py skills build openai_azure --nocache
    python3 client.py skills run openai_azure --url <broker_url> --api_key <openai_api_key> --api_endpoint <openai_endpoint> --skill <skill_name>

Llama.cpp
~~~~~~~~~

This skill supports the Llama.cpp API through the llama-cpp-python wrapper.
For more details follow `llama-cpp-python <https://llama-cpp-python.readthedocs.io/en/latest/>`_.

.. code-block:: bash

    python3 client.py skills build llama.cpp --nocache
    python3 client.py skills run llama.cpp --url <broker_url> --skill <skill_name> --model_path <model_path>