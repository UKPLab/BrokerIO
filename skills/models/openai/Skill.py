import os

from SkillSimple import SkillSimple
from openai import OpenAI


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
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    def execute(self, data):
        """
        Execute a request to the OpenAI API
        :param data:
        :return:
        """
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": data['data']['role'] if 'role' in data['data'] else 'user',
                    "content": data['data']['prompt']
                }
            ],
            model="gpt-3.5-turbo"
        )
        return {'id': data['id'], 'data': chat_completion}

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
                'role': {
                    'type': 'string',
                    'required': False,
                    'default': 'user'
                }
            },
            'example': {
                'prompt': 'Say this is a test',
                'role': 'user'
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
