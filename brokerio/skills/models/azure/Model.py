""" Skill for OpenAI Azure Client

This skill is a simple wrapper for the OpenAI Azure Client.

Documentation Azure Client
https://learn.microsoft.com/en-us/azure/ai-services/openai/quickstart?tabs=command-line%2Cpython-new&pivots=programming-language-python

Author: Dennis Zyska
"""

from brokerio.skills.SkillModel import SkillModel


class Model(SkillModel):

    def run(self, additional_parameter=None):
        """
        Run the skill
        :param additional_parameter:
        :return:
        """
        super().run({
            "environment": {
                'AZURE_OPENAI_KEY': self.args.api_key,
                'AZURE_OPENAI_ENDPOINT': self.args.api_endpoint,
                'OPENAI_MODEL': self.args.model,
                'API_VERSION': "2023-05-15" if self.args.model == "gpt-4" else "2023-10-01-preview",
                'OPENAI_API_TYPE': "azure",
            },
        })

    @staticmethod
    def arg_parser(parser):
        parser.add_argument('--api_key', help='OpenAI API Key', required=True)
        parser.add_argument('--api_endpoint', help='OpenAI API Endpoint', default='https://api.openai.com')
        parser.add_argument('--model', help='OpenAI Model (Default: gpt-35-turbo-0301',
                            default='gpt-35-turbo-0301')
