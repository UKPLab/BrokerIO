.. NLP API documentation master file, created by
   sphinx-quickstart on Fri Dec  2 15:55:21 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to NLP Broker's documentation!
======================================

The NLP Broker should provide a simple interface to a variety of NLP tools and models.
It is designed to be used by the NLP Broker API based on websockets.

NLP tools and models are registered as skills and can then be used by the API.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting_started/quickstart
   getting_started/installation
   getting_started/development

.. toctree::
   :maxdepth: 2
   :caption: Skills
   :hidden:

   skills/skill_definition_file


DISCLAIMER
----------
This component is under continuous development and refactoring. Specifically, the following features are not implemented
yet, although they might be referenced in the following documentation:

- adding a gunicorn (or any WSGI server) in-front of the flask app
- structuring of the server components using:
- Blueprints for flask routes (checkout documentation on that)
- Celery task registry (checkout documentation on that)
- Flower does not connect properly yet (for monitoring Celery)

