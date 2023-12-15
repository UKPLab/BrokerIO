Available models
================

The broker also provides some basic models that can be published as a skill.
The models can be published via the CLI client :doc:`CLI </broker/client>`.
The following models are available:

OpenAI Azure
~~~~~~~~~~~~

This skill supports the OpenAI Azure API. For more details follow `Quickstart <https://learn.microsoft.com/en-us/azure/ai-services/openai>`_.

Example to run the skill:

.. code-block:: bash

    python3 client.py skills build openai_azure --nocache
    python3 client.py skills run openai_azure --url <broker_url> --api_key <openai_api_key> --api_endpoint <openai_endpoint> --skill <skill_name>

