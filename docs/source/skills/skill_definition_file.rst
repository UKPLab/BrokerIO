Skill Definition File
=====================

Skill Definition File (SDF) is a file format for defining skills for use in this API.
The files describe the basic input and output of a model provided by a skill.
It also describes the skill's metadata, such as the name, description, and version in
a human-readable and machine-readable format.

**Examples:** A list of example SDF files can be found in the `sdf` directory of the repository.

SDF Basics
----------

The SDF should be easily readable by humans and machines, therefore is is based on the YAML format for several reasons:

* YAML is a human-readable format
* YAML is a machine-readable format
* YAML is a `natural superset <http://yaml.org/spec/1.2-old/spec.html#id2759572>`_ of JSON, a common format for machine-readable data
* YAML supports also references, which are useful for defining the same data in multiple places
* YAML is supported by Python through `PyYAML <http://pyyaml.org/>`_

SDF Template
------------

The SDF template is a YAML file that contains the basic structure of an SDF file.

.. code-block:: yaml

    # SDF template
    name: <name of the task>
    description: <description of the task>
    needs: []
    config: # see sections
     data:
      labels:
       type: <type_array>
       required: true
       default: [true, false]
       array:
        type: <type_boolean>
        required: true
     example: [true, false]
     required: false # only if config needed for each request from frontend
    input:
     data:
      text_input:
       type: <type_object>
       required: true
       object:
        key:
         type: <type_string>
         description: Object element with key "key"
         default: "value"
         required: True
     example: {text_input: {key: "value"}}
    output:
     data:
      score:
       type: <type_float>
       default: 0
       description: Prediction Score
      start:
       type: <type_int>
       description: Start position
      end:
       type: <type_int>
       description: End position
      answer:
       type: <type_string>
       description: Answer of the task
     example: {score: 1.0, start: 2, end: 10, answer: "Yes of course"}

.. note::

    The SDF template is not a valid SDF file. It is only a template to show the structure of an SDF file.

    Also, if the model need further configuration, of course the YAML can be extended.

Types
-----

The SDF template uses the following types:

* ``<type_string>``: A string
* ``<type_int>``: An integer
* ``<type_float>``: A float
* ``<type_boolean>``: A boolean
* ``<type_array>``: An array
* ``<type_object>``: An object

.. note::

    The types are not defined in the YAML specification. They are only used in this API to describe the types of the data.

    The types for arrays and objects needs further definitions, for array with key array and for objects with key object (see example).

Sections
--------

The SDF template contains the following sections:

.. list-table::

 * - **Section**
   - **Description**
 * - config
   - | Configuration of the model, the parameter required can be used,
     | if the parameters should set with each input separately during runtime.
 * - input
   - Input of the model, the input data is defined in the data section.
 * - output
   - Output of the model, the output data is defined in the data section.
 * - needs
   - | List of task that should be handles by the broker before running the own task,
     | because we want not provide it by the own model. The order matters!
     | This task has to be published to the broker, otherwise the job will wait forever to finish!


.. note::

        If using the config section, the config data will be provided with each input separately during runtime.

        Make sure the models can handle this very fast, otherwise is better to provide several models to reduce inference time!