""" Skill for OpenAI Azure Client

This skill is a simple wrapper for the OpenAI Azure Client.

Documentation Azure Client
https://learn.microsoft.com/en-us/azure/ai-services/openai/quickstart?tabs=command-line%2Cpython-new&pivots=programming-language-python

Author: Dennis Zyska
"""

import os

from SkillSimple import SkillSimple
from openai import AzureOpenAI


class Skill(SkillSimple):
    """
    Skill for OpenAI API
    """

    def __init__(self, name):
        super().__init__(name)
        self.description = "This is a skill for the OpenAI API"
        self.client = None

    def init(self):
        """
        Initialize Open AI Connection
        :return:
        """
        self.client = AzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_KEY"),
            api_version=os.environ.get("API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        # OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    def execute(self, data):
        """
        Execute a request to the OpenAI API
        :param data:
        :return:
        """
        response = self.client.completions.create(model=os.environ.get('OPENAI_MODEL'), prompt=data['prompt'],
                                                  max_tokens=data['max_tokens'] if 'max_tokens' in data else 10)
        output = {
            "response": [c.__dict__ for c in response.choices],
        }
        stats = {
            "id": response.id,
            "created": response.created,
            "model": response.model,
            "object": response.object,
            "filter": [c.content_filter_results for c in response.choices],
            "fingerprint": response.system_fingerprint,
            "usage": response.usage.__dict__,
        }
        return output, stats

    def get_input(self):
        """
        Get the input schema
        :return:
        """
        return {
            'data': {
                'prompt': {
                    'type': 'string',
                    'required': True
                },
                'max_tokens': {
                    'type': 'integer',
                    'required': False,
                    'default': 10
                }
            },
            'example': {
                'prompt': 'Once a while'
            }
        }

    def get_output(self):
        """
        Get the output schema
        :return:
        """
        return {
            'data': {
                'response': {
                    'type': 'array',
                    'items': {
                        'type': "object",
                        "properties": {
                            "finish_reason": {
                                "type": 'string',
                            },
                            'index': {
                                "type": 'integer',
                            },
                            'logprops': {
                                "type": 'object',
                            },
                            'text': {
                                "type": "string"
                            },
                            'filter': {
                                "type": "array",
                                "description": "Same size a responses with safety information (content filter)"
                            },
                            'fingerprint': {
                                "type": "string"
                            }
                        }
                    },
                }
            },
            'stats': {
                'type': 'object',
                'properties': {
                    'id': {
                        "type": "string"
                    },
                    'created': {
                        "type": "integer"
                    },
                    'model': {
                        "type": "string"
                    },
                    'object': {
                        "type": "string"
                    },
                    'usage': {
                        "type": "object",
                        "properties": {
                            "completion_tokens": {
                                "type": "integer"
                            },
                            "prompt_tokens": {
                                "type": "integer"
                            },
                            "total_tokens": {
                                "type": "integer"
                            }
                        }
                    }
                }
            },
            'example': {
                "response": [{'finish_reason': 'length', 'index': 0, 'logprobs': None, 'text': ', quite long ago,'}]
            }
        }
