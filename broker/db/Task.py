import time


class Task:
    def __init__(self, task_id, request_id, session_id):
        self.session_id = session_id
        self.request_id = request_id
        self.id = task_id
        self.start_time = time.perf_counter()
