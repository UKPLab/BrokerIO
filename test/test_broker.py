import logging
import multiprocessing as mp
import os
import time
import unittest

from broker import init_logging
from broker.app import init
from utils import simple_response_container, simple_client


class TestBroker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logger = init_logging(name="Unittest", level=logging.DEBUG)
        cls._logger = logger

        logger.info("Starting response container ...")
        ctx = mp.get_context('spawn')
        container = ctx.Process(target=simple_response_container, args=(
            "http://{}:{}".format(os.getenv("BROKER_HOST"), os.getenv("BROKER_PORT")), os.getenv("BROKER_TOKEN"),
            "test_skill"))
        container.start()
        cls._container = container

        logger.info("Starting broker ...")
        if os.getenv("BROKER_HOST") != "localhost" and os.getenv("BROKER_HOST") != "127.0.0.1":
            logger.info("Broker is not running on localhost. Skip creating broker.")
        else:
            ctx = mp.get_context('spawn')
            broker = ctx.Process(target=init, args=())
            broker.start()
            cls._broker = broker

        logger.info("Start client ...")
        client_queue = mp.Manager().Queue(10)
        message_queue = mp.Manager().Queue(10)
        client = ctx.Process(target=simple_client, args=(
            "http://{}:{}".format(os.getenv("BROKER_HOST"), os.getenv("BROKER_PORT")), os.getenv("BROKER_TOKEN"),
            "test_skill", client_queue, message_queue))
        client.start()
        cls._client = client
        cls._message_queue = message_queue
        cls._client_queue = client_queue

        # Waiting until environment is ready
        logger.info("Waiting for environment to be ready ...")
        message = client_queue.get()
        logger.debug("Main process received message: {}".format(message))
        logger.info("Environment ready!")

    @classmethod
    def tearDownClass(cls):
        cls._logger.info("Stopping client ...")
        cls._client.terminate()
        cls._client.join()

        cls._logger.info("Stopping response container ...")
        cls._container.terminate()
        cls._container.join()

        cls._logger.info("Stopping broker ...")
        if os.getenv("BROKER_HOST") != "localhost" and os.getenv("BROKER_HOST") != "127.0.0.1":
            cls._logger.info("Broker is not running on localhost. Skip stopping broker.")
        else:
            cls._broker.terminate()
            cls._broker.join()

    def test_simple_request(self):

        ## Test simple response
        self._message_queue.put({'id': "simple", 'name': "test_skill", 'data': time.perf_counter()})

        self._logger.info("Wait for response ...")

        message = self._client_queue.get()

        self._logger.info("Simple response time: {:3f}ms".format((time.perf_counter() - message['data']) * 1000))
        self.assertEqual(message['id'], "simple")


if __name__ == '__main__':
    unittest.main()
