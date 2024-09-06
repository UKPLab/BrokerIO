import logging
import multiprocessing as mp

from brokerio import init_logging
from brokerio.utils import simple_client


class Guard:
    """
    Guard is a simple client that connects to the broker and listen to broadcast messages.

    @author: Dennis Zyska
    """

    def __init__(self, url):
        self.url = url
        self.logger = init_logging("Guard", logging.DEBUG)
        self.client = None
        self.client_queue = None

    def run(self):
        self.logger.info("Start guard ...")
        ctx = mp.get_context('spawn')
        self.client_queue = mp.Manager().Queue(12)
        message_queue = mp.Manager().Queue(12)
        self.client = ctx.Process(target=simple_client, args=("Guard",
                                                              self.url, self.client_queue, message_queue))
        self.client.start()

    def join(self):
        while True:
            message = self.client_queue.get()
            self.logger.info("Guard received message: {}".format(message))
