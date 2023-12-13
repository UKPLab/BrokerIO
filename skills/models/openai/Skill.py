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
        print("Using model: {}".format(os.environ.get('OPENAI_MODEL')))
        response = self.client.completions.create(model=os.environ.get('OPENAI_MODEL'), prompt=data['prompt'],
                                                  max_tokens=data['max_tokens'] if 'max_tokens' in data else 10)
        return response

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
                'prompt': 'Say this is a test'
            }
        }

    def get_output(self):
        """
        Get the output schema
        :return:
        """
        return {
            'data': {
                'id': {
                    'type': 'string',
                },
                'data': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'string'
                        },
                        'object': {
                            'type': 'string'
                        },
                        'created': {
                            'type': 'integer'
                        },
                        'model': {
                            'type': 'string'
                        },
                        'usage': {
                            'type': 'object',
                            'properties': {
                                'prompt_tokens': {
                                    'type': 'integer'
                                },
                                'completion_tokens': {
                                    'type': 'integer'
                                },
                                'total_tokens': {
                                    'type': 'integer'
                                }
                            }
                        },
                        'choices': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'message': {
                                        'type': 'object',
                                        'properties': {
                                            'role': {
                                                'type': 'string'
                                            },
                                            'content': {
                                                'type': 'string'
                                            }
                                        }
                                    },
                                    'finish_reason': {
                                        'type': 'string'
                                    },
                                    'index': {
                                        'type': 'integer'
                                    }
                                }
                            }
                        }
                    }
                }
            },
            'example': {
                'id': 'chatcmpl-abc123',
                'data': {
                    "id": "chatcmpl-abc123",
                    "object": "chat.completion",
                    "created": 1677858242,
                    "model": "gpt-3.5-turbo-1106",
                    "usage": {
                        "prompt_tokens": 13,
                        "completion_tokens": 7,
                        "total_tokens": 20
                    },
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "\n\nThis is a test!"
                            },
                            "finish_reason": "stop",
                            "index": 0
                        }
                    ]
                }
            }
        }
