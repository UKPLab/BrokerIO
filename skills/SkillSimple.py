class SkillSimple:
    def __init__(self, config):
        self.config = config

    def init(self):
        """
        Initialize the skill
        :return:
        """
        pass

    def get_config(self):
        """
        Register the skill at the broker
        :return: None
        """
        return self.config

    def execute(self, data):
        """
        Execute the skill
        :param data: data object from the broker
        :return: result object
        """
        return data
