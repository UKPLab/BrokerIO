import logging
import multiprocessing as mp
import queue
import time

import socketio

from broker import init_logging
from broker.utils.Keys import Keys


def client(name, url, in_queue: mp.Queue, out_queue: mp.Queue):
    logger = init_logging(name, level=logging.getLevelName("INFO"))
    sio = socketio.Client(logger=logger, engineio_logger=logger)

    @sio.on('*')
    def catch_all(event, data):
        out_queue.put({"event": event, "data": data})

    sio.on('connect', lambda: [out_queue.put({"event": "connected", "data": {}})])

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


class TestClient:
    """
    Example client for testing
    @author: Dennis Zyska
    """

    def __init__(self, logger, url, queue_size=200, name="Simple Client"):
        self.url = url
        self.logger = logger
        self.in_queue = mp.Manager().Queue(queue_size)
        self.out_queue = mp.Manager().Queue(queue_size)
        self.skills = []
        self.client = None
        self.name = name

    def start(self):
        self.logger.info("Start auth client ...")
        ctx = mp.get_context('spawn')
        self.client = ctx.Process(target=client, args=(self.name, self.url, self.in_queue, self.out_queue))
        self.client.start()

        return self.wait_for_event("connected", timeout=30)

    def auth(self, private_key_path="./private_key.pem"):
        keys = Keys(private_key_path=private_key_path)

        # send auth request
        self.put({"event": "authRequest", "data": {}})

        # wait for auth challenge
        challenge = self.wait_for_event("authChallenge")
        self.logger.error(challenge)
        if challenge:
            sig = keys.sign(challenge['data']['secret'])
            self.put({"event": "authResponse", "data": {'pub': keys.get_public(), 'sig': sig}})

            # return auth info
            return self.wait_for_event("authInfo")
        else:
            return False

    def wait_for_event(self, event, timeout=5):
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
                self.logger.error(m['data'])
            if 'event' in m and m['event'] == "skillUpdate":
                self.skills = m['data']
            return m
        except queue.Empty:
            return False

    def get(self, *args, **kwargs):
        return self.out_queue.get(*args, **kwargs)

    def clear(self):
        """
        Clear all messages in the queues
        :return:
        """
        while not self.out_queue.empty():
            self.out_queue.get()

    def stop(self):
        if self.client:
            self.logger.info("Kill client ...")
            self.client.terminate()
            self.client.join()
