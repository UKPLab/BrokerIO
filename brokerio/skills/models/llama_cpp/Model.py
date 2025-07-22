""" Skill for Llama.cpp Models

This skill is a simple wrapper for the LLama.cpp python client

https://llama-cpp-python.readthedocs.io/en/latest/

Author: Dennis Zyska
"""
import os

from brokerio.skills.SkillModel import SkillModel


class Model(SkillModel):

    def run(self, additional_parameter=None):
        """
        Run the skill
        :param additional_parameter:
        :param args:
        :return:
        """
        model_path, model_file = os.path.split(self.args.model_path)

        super().run({
            "environment": {
                'MODEL_PATH': os.path.join("/model", model_file),
                'N_THREADS': self.args.n_threads,
                'NUM_CTX': self.args.n_ctx,
            },
            "volumes": {
                model_path: {'bind': '/model', 'mode': 'ro'},
            }
        })

    @staticmethod
    def arg_parser(_parser):
        _parser.add_argument('--model_path', help='Llama.cpp model', required=True)
        _parser.add_argument('--n_threads', help='Number of threads for llama.cpp', type=int, default=30)
        _parser.add_argument('--n_ctx', help='Contexts length for llama.cpp', type=int, default=512)
