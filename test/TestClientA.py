import logging
import multiprocessing as mp
import queue
import time

import socketio

from broker import init_logging


def client(url, in_queue: mp.Queue, out_queue: mp.Queue):
    logger = init_logging("Simple Client", level=logging.getLevelName("INFO"))
    sio = socketio.Client(logger=logger, engineio_logger=logger)

    @sio.on('*')
    def catch_all(event, data):
        logger.error("Event: {} - Data: {}".format(event, data))
        out_queue.put({"event": event, "data": data})

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


class TestClientA:
    def __init__(self, logger, url, queue_size=200):
        self.url = url
        self.logger = logger
        self.in_queue = mp.Manager().Queue(queue_size)
        self.out_queue = mp.Manager().Queue(queue_size)
        self.client = None

    def start(self):
        self.logger.info("Start auth client ...")
        ctx = mp.get_context('spawn')
        self.client = ctx.Process(target=client, args=(self.url, self.in_queue, self.out_queue))
        self.client.start()

    def put(self, message):
        self.in_queue.put(message)

    def check_queue(self):
        """
        Check if the client queue has elements
        :return: message if queue is not empty, otherwise None
        """
        try:
            m = self.out_queue.get(block=False)
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
