import os


class Skill:
    def __init__(self):
        self.description = "This is just a template for a simple skill"
        self.features = None
        self.sio = None

    def init(self):
        """
        Initialize the skill
        :return:
        """
        pass

    def set_sio(self, sio):
        """
        Set the socket io instance
        :param sio: socket io instance
        :return: None
        """
        self.sio = sio

    def send_status(self, task_id, status):
        """
        Send status to the broker
        :param task_id: task id of the current task
        :param status: status object
        :return: None
        """
        if self.features is not None and 'status' in self.features:
            self.sio.emit('taskResults', {'id': task_id, "status": "running", 'data': {'status': status}})
        else:
            raise Exception("Feature 'status' not supported by this skill, activate it in the constructor")

    def get_config(self):
        """
        Register the skill at the broker
        :return: None
        """
        config = {
            'name': os.environ.get('SKILL_NAME'),
            'description': self.description,
            'input': self.get_input(),
            'output': self.get_output()
        }
        if self.features is not None:
            config['features'] = self.features
        return config

    def execute(self, task_id, data):
        """
        Execute the skill
        :param task_id: task id of the current task
        :param data: data object from the broker
        :return: result object
        """
        return data, None

    def get_input(self):
        """
        Get the input schema
        :return:
        """
        return {
            'data': {
                '*': {
                    'type': 'string',
                    'required': True
                }
            },
            'example': {
                {'anything': 'Hello World'}
            }
        }

    def get_output(self):
        """
        Get the output schema
        :return:
        """
        return {
            'data': {
                '*': {
                    'type': 'string',
                    'required': True
                }
            },
            'example': {
                'anything': 'Hello World'
            }
        }
