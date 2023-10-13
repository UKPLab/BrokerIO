import logging
import multiprocessing as mp
import queue
import time

import socketio

from broker import init_logging
from broker.utils.Keys import Keys
from collections import deque


def client_process(name, url, in_queue: mp.Queue, out_queue: mp.Queue):
    logger = init_logging(name, level=logging.getLevelName("INFO"))
    sio = socketio.Client(logger=logger, engineio_logger=logger)

    @sio.on('*')
    def catch_all(event, data):
        out_queue.put({"event": event, "data": data})

    sio.on('connect', lambda: [out_queue.put({"event": "connected", "data": {}})])

    # always send task requests back to broker

    @sio.on('taskRequest')
    def task_request(data):
        out_queue.put({"event": "taskRequest", "data": data})
        if isinstance(data['data'], dict) and 'sleep' in data['data']:
            time.sleep(data['data']['sleep'])
        sio.emit('taskResults', {"id": data["id"], "data": data['data']})

    while True:
        try:
            if sio.connected:
                logger.debug("Waiting for next message...")
                message = in_queue.get()
                sio.emit(message['event'], message['data'])
                logger.debug("Send message: {}".format(message))
            else:
                sio.connect(url)
        except socketio.exceptions.ConnectionError:
            logger.error("Connection to broker failed. Trying again in 5 seconds ...")
            time.sleep(5)


class Client:
    """
    Example API Client for testing
    @author: Dennis Zyska
    """

    def __init__(self, url, queue_size=200, buffer_size=300, name="Simple Client", logger=None):
        self.url = url
        self.logger = logger
        self.in_queue = mp.Manager().Queue(queue_size)
        self.out_queue = mp.Manager().Queue(queue_size)
        self.skills = []
        self.client = None
        self.role = "guest"
        self.results_buffer = deque(maxlen=buffer_size)
        self.name = name

    def start(self):
        if self.logger is not None:
            self.logger.info("Start auth client ...")
        ctx = mp.get_context('spawn')
        self.client = ctx.Process(target=client_process, args=(self.name, self.url, self.in_queue, self.out_queue))
        self.client.start()

        return self.wait_for_event("connected", timeout=30)

    def auth(self, private_key_path="./private_key.pem"):
        keys = Keys(private_key_path=private_key_path)

        # send auth request
        self.put({"event": "authRequest", "data": {}})

        # wait for auth challenge
        challenge = self.wait_for_event("authChallenge")
        if self.logger is not None:
            self.logger.error(challenge)
        if challenge:
            sig = keys.sign(challenge['data']['secret'])
            self.put({"event": "authResponse", "data": {'pub': keys.get_public(), 'sig': sig}})

            # return auth info
            auth_info = self.wait_for_event("authInfo")
            if auth_info:
                self.role = auth_info['data']['role']
                return auth_info
            else:
                return False
        else:
            return False

    def wait_for_event(self, event, timeout=10):
        """
        Wait for a specific event
        :param event: event name
        :param timeout: timeout in seconds
        :return:
        """
        start = time.time()
        while time.time() - start < timeout:
            m = self.check_queue()
            if m:
                if m['event'] == event:
                    return m
            else:
                time.sleep(0.1)
        return False

    def put(self, message):
        self.in_queue.put(message)

    def check_queue(self):
        """
        Check if the client queue has elements
        :return: message if queue is not empty, otherwise None
        """
        try:
            m = self.out_queue.get(block=False)
            if 'event' in m and m['event'] == "error":
                if self.logger is not None:
                    self.logger.error(m['data'])
            if 'event' in m and m['event'] == "skillUpdate":
                new_skills = m['data']
                for skill in new_skills:
                    self.update_skills(skill)
            if 'event' in m and m['event'] == "skillResults":
                self.results_buffer.append(m['data'])
            return m
        except queue.Empty:
            return False

    def check_skill(self, skill):
        """
        Check if skill is available
        :param skill: name of the skill
        :return:
        """
        self.clear()
        return next((i for i, s in enumerate(self.skills) if s['name'] == skill), None) is not None

    def update_skills(self, skill):
        """
        Update skill list with new skill
        :param skill: skill to update
        :return:
        """
        # find position of skill in list
        idx = next((i for i, s in enumerate(self.skills) if s['name'] == skill['name']), None)
        if idx is not None:
            if skill['nodes'] == 0:
                del self.skills[idx]
            else:
                self.skills[idx]['nodes'] = skill['nodes']
                if 'config' in skill:
                    self.skills[idx]['config'] = skill['config']
        else:
            self.skills.append(skill)

    def find_results(self, id):
        """
        Find results in the queue
        :param id: id of the request
        :return: results if found, otherwise None
        """
        # add all results to the buffer
        while self.check_queue():
            pass

        # check if there are results in the buffer
        try:
            return next(i for i in self.results_buffer if i['id'] == id)
        except StopIteration:
            return None

    def get(self, *args, **kwargs):
        return self.out_queue.get(*args, **kwargs)

    def clear(self):
        """
        Clear all messages in the queues
        :return:
        """
        while not self.out_queue.empty():
            self.check_queue()

    def stop(self):
        if self.client:
            if self.logger is not None:
                self.logger.info("Kill client ...")
            self.client.terminate()
            self.client.join()
