""" Skill for the Huggingface Pipeline

This skill is a simple wrapper for the Huggingface Pipeline:

https://huggingface.co/docs/transformers/main_classes/pipelines

Author: Dennis Zyska
"""
import inspect
import os
import pathlib

from brokerio.skills.SkillModel import SkillModel


class Model(SkillModel):
    def run(self, args, additional_parameter=None):
        """
        Run the skill
        :param additional_parameter:
        :param args:
        :return:
        """
        super().run(args, {
            "environment": {
                'TASK': args.task,
                'MODEL': args.model,
                'CUDA_DEVICE': args.cuda,
            },
        })

    @staticmethod
    def arg_parser(_parser):
        tasks_files = os.listdir(
            os.path.join(pathlib.Path(inspect.getfile(inspect.currentframe())).resolve().parent, 'tasks'))
        tasks = [os.path.splitext(file)[0] for file in tasks_files if file.endswith('.yaml')]

        _parser.add_argument('--task', help='Huggingface pipeline task', choices=tasks, required=True)
        _parser.add_argument('--model', help='Overwrite basic huggingface pipeline model', default="")
        _parser.add_argument('--cuda', help='CUDA device', default=-1, type=int)
