
import multiprocessing as mp
from time import sleep
from broker.utils import simple_client
import logging
from broker import init_logging

class Guard:
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.logger = init_logging("Guard", logging.DEBUG)

    def run(self):

        self.logger.info("Start guard ...")
        ctx = mp.get_context('spawn')
        client_queue = mp.Manager().Queue(12)
        message_queue = mp.Manager().Queue(12)
        client = ctx.Process(target=simple_client, args=(
            self.url, self.token, client_queue, message_queue))
        client.start()

        while True:
            message = client_queue.get()
            self.logger.info("Guard received message: {}".format(message))
