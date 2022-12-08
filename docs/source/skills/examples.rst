SDF Examples
============

Here we would like to show a few examples how a skill definition file can look like

Sentiment Classification
------------------------

.. code-block::
    yaml

    name: sentiment-classification
    description: This is a classification task for semtiment classification
    needs: []
    config:
      data:
        task:
          type: String
          description: The task to be performed by the transformer pipeline
          default: "text-classification"
          required: true
        model:
          type: String
          description: The model to be used by the transformer pipeline
          default: "allenai/scibert_scivocab_uncased"
          required: true
        labels:
          type: Array
          description: The labels to be used by the transformer pipeline
          default: ['positive', 'negative']
          array: String
          required: true
      required: false
      example: {task: "text-classification", model: "allenai/scibert_scivocab_uncased", labels: ['positive', 'negative']}
    input:
      data:
        text:
          type: String
          required: true
          description: The text to be classified
        required: true
      example: {text: "This is a test"}
    output:
      data:
        score:
          type: Number
          description: The score of the classification
        label:
          type: String
          description: The label of the classification
      example: {score: 0.9, label: "positive"}

