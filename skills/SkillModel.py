from broker.cli import CLI
from skills.templates.simpleSkill import create_docker as build_simple_skill


class SkillModel(CLI):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.tag = 'broker_skill_' + self.name
        self.template = "simpleSkill"

    def set_parser(self, parser):
        self.parser = parser

    def build(self, nocache=False):
        """
        Build the docker container
        :param nocache: Do not use cache
        :return:
        """
        if self.template is None:
            print("No template defined")
            exit()
        if self.template == "simpleSkill":
            build_simple_skill(nocache=nocache)
