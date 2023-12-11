import os

from SkillSimple import SkillSimple
from openai import OpenAI


class Skill(SkillSimple):
    """
    Skill for OpenAI API
    """

    def __init__(self, config):
        super().__init__(config)
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
                    "role": data['data']['role'],
                    "content": data['data']['prompt']
                }
            ],
            model="gpt-3.5-turbo"
        )
        return {'id': data['id'], 'data': chat_completion}
