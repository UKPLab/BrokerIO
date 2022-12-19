import time
from uuid import uuid4


class Task:
    def __init__(self, client_session):
        self.client_session = client_session
        self.id = str(uuid4())

        self.config = None
        self.request_id = None
        self.results = None
        self.time_start = time.perf_counter()
        self.time_last_update = self.time_start
        self.duration = None

    def set(self, data):
        if "config" in data:
            self.config = data['config']
        self.request_id = data['id']
        self.time_last_update = time.perf_counter()

    def set_score(self, data):
        """
        Set the results data of the task from container
        :param data: the output field in SDF format
        :return:
        """
        self.results = data
        self.duration = time.perf_counter() - self.time_start

    def output(self):
        """
        Return the output of the task
        :return: output object as send to the client
        """
        output = {
            'id': self.request_id,
            'data': self.results['data']
        }
        if self.config and 'return_stats' in self.config:
            output['stats'] = {
                'duration': self.duration
            }
        return output

    def close(self):
        """
        Finish the task - delete it from the list of current tasks
        :return:
        """
        del self
