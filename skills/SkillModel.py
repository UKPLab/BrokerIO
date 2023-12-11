from broker.cli import CLI


class SkillModel(CLI):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.tag = 'broker_skill_' + self.name

    def set_parser(self, parser):
        self.parser = parser
