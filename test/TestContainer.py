import multiprocessing as mp
import os

from test import simple_response_container


class TestContainer:
    def __init__(self, logger, url, token, skill_name, roles=None, name="TestContainer"):
        self.logger = logger
        self.url = url
        self.token = token
        self.queue = mp.Manager().Queue(10)
        self.skill_name = skill_name
        self.container = None
        self.name = name
        self.roles = roles if roles else []

    def start(self):
        self.logger.info("Start new container ...")
        ctx = mp.get_context('spawn')
        self.container = ctx.Process(target=simple_response_container, args=(
            self.name, self.url, self.token,
            self.skill_name, self.queue, self.roles, os.getenv("TEST_CONTAINER_LOGGING_LEVEL", "ERROR")))

        self.container.start()

        self._wait_for_start()

    def _wait_for_start(self):
        while True:
            message = self.queue.get()
            self.logger.info("Client received message: {}".format(message))
            if message == "connected":
                return True

    def stop(self):
        if self.container:
            self.logger.info("Kill container ...")
            self.container.terminate()
            self.container.join()
