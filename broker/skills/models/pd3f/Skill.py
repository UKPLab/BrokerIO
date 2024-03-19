""" Skill for PD3F PDF text extraction

This skill is a simple skill that uses the PD3F PDF text extraction tool to extract text from a PDF file.

https://github.com/pd3f/pd3f
https://pd3f.github.io/pd3f-core/export.html#pd3f.export.extract

Author: Dennis Zyska
"""

import os
import time

from pd3f import extract
from SkillSimple import SkillSimple
import logging
import base64

logging.basicConfig(level=logging.INFO)


class Skill(SkillSimple):
    """
    Skill for OpenAI API
    """

    def __init__(self, name):
        super().__init__(name)
        self.description = "This is a pdf text extraction skill based on pd3f"
        self.tmp_file = "/app/pd3f.pdf"

    def init(self):
        """
        Initialize Open AI Connection
        :return:
        """
        pass

    def execute(self, data):
        """
        Execute a request to the OpenAI API
        :param data:
        :return:
        """
        start = time.perf_counter()
        # data['pdf'] is base64 encoded --> save to file
        content = base64.b64decode(data['pdf'])
        with open(self.tmp_file, 'wb') as f:
            f.write(content)

        text, tables = extract(self.tmp_file,
                               parsr_location="{}_{}:3001".format(os.environ.get("CONTAINER_NAME"), 'parsr'),
                               **data['params'])

        stats = {
            'duration': time.perf_counter() - start
        }

        logging.info(text)
        logging.info(tables)

        return text, stats

    def get_input(self):
        """
        Get the input schema
        :return:
        """
        return {
            'data': {
                'pdf': {
                    'type': 'string',
                    'description': 'Base64 encoded PDF file'
                },
                'params': {
                    'type': 'object',
                    'description': 'Additional parameters for the pd3f extraction',
                    'required': False,
                    'properties': {
                        'tables': {
                            'type': 'boolean',
                            'description': 'extract tables via Parsr (with Camelot / Tabula), results into list of CSV strings'
                        },
                        'experimental': {
                            'type': 'boolean',
                            'description': 'leave out duplicate text in headers / footers and turn footnotes to endnotes. Working unreliable right now'
                        },
                        'lang': {
                            'type': 'string',
                            'description': 'set the language, de for German, en for English, es for Spanish, fr for French. Some fast (less accurate) models exists. So set multi-v0-fast to get fast model for German, French (and some other languages)'
                        },
                        'fast': {
                            'type': 'boolean',
                            'description': 'Drop some Parsr steps to speed up computations'
                        },
                    }
                },
            },
            'example': {
                "pdf": "base64 encoded pdf",
                "params": {
                    "tables": True,
                    "experimental": False,
                    "lang": "en",
                    "fast": False
                }
            }
        }

    def get_output(self):
        """
        Get the output schema
        :return:
        """
        return {
            'data': {
            },
            'stats': {
                'type': 'object',
                'properties': {
                    'id': {
                        "type": "string"
                    },
                    'duration': {
                        "type": "number",
                        "description": "Duration of executing azure api in seconds"
                    }
                }
            },
            'example': {
                'stats': {
                    'result': {'id': '123', 'duration': 0.123}
                }
            }
        }
