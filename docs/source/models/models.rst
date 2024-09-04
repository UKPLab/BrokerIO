Available models
================

The broker also provides some basic models that can be published as a skill.
The models can be published via the CLI client :doc:`CLI </broker/client>`.

.. tip::

    Always use the ``--help`` option to get an overview of the available options, as each model has different requirements.

.. note::

    If the broker is running in a local docker container (e.g. during development), the models needs to be added to the same network. This allows to access via the container name in the URL. `localhost` does not work, as it would connect only to the own skill's docker machine. You can set the network via ``--network`` option.

Build Models
------------

Before we can use any of the models, we need to build them. This is done by running the following command:

.. code-block:: bash

    brokerio skills build <model_name> --nocache

Run Models
----------

After building the model, we can run it. Therefore, the following options are available for all models:

- ``--url``: The broker URL.
- ``--skill``: The skill name.
- ``--network``: The network name of the broker container.
- ``--num_containers``: The number of containers to run the skill.
- ``--container_suffix``: The suffix for the container name.

Individual models may have additional options. Please refer to the help of the model for more information.

Models
------

In the following, we will introduce the available models.

OpenAI Azure
~~~~~~~~~~~~

This skill supports the OpenAI Azure API. For more details follow `Quickstart <https://learn.microsoft.com/en-us/azure/ai-services/openai>`_.

Example to run the skill:

.. code-block:: bash

    brokerio skills build openai_azure --nocache
    brokerio skills run openai_azure --url <broker_url> --api_key <openai_api_key> --api_endpoint <openai_endpoint> --skill <skill_name>

Llama.cpp
~~~~~~~~~

This skill supports the Llama.cpp API through the llama-cpp-python wrapper.
For more details follow `llama-cpp-python <https://llama-cpp-python.readthedocs.io/en/latest/>`_.

.. code-block:: bash

    brokerio skills build llama.cpp --nocache
    brokerio skills run llama.cpp --url <broker_url> --skill <skill_name> --model_path <model_path>

Huggingface Transformer Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This skill supports the Huggingface Transformer Pipeline API.
For more details follow `Pipeline tutorial <https://huggingface.co/docs/transformers/pipeline_tutorial>`_.

The following tasks are supported:

- ``fill-mask``
- ``question-answering``
- ``text-classification``
- ``summarization``
- ``translation_en_to_de``
- ``text-generation``
- ``text2text``

.. tip::

    See the folder ``./broker/skills/models/hf_pipeline/tasks`` for examples.

.. code-block:: bash

    brokerio skills build hf_pipeline --nocache
    brokerio skills run hf_pipeline --url <broker_url> --skill <skill_name> --model <model_name> --task <task>

Vader Sentiment Analysis
~~~~~~~~~~~~~~~~~~~~~~~~

This skill supports the Vader Sentiment Analysis. For more details follow `Vader Sentiment Analysis <https://www.nltk.org/_modules/nltk/sentiment/vader.html>`_.

.. code-block:: bash

    brokerio skills build vader --nocache
    brokerio skills run vader --url <broker_url> --skill <skill_name>
