import json
import logging
import multiprocessing as mp
import os
import queue
import time
import unittest

from broker import init_logging
from broker.app import init
from broker.utils import simple_client
from broker.utils.Guard import Guard
from utils import simple_response_container


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
            client_queue, message_queue, "test_skill"))
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
        """
        Test if simple request is working
        :return:
        """

        ## Test simple response
        self._message_queue.put({'id': "simple", 'name': "test_skill", 'data': time.perf_counter()})

        self._logger.info("Wait for response ...")

        message = self._client_queue.get()

        self._logger.info("Simple response time: {:3f}ms".format((time.perf_counter() - message['data']) * 1000))
        self.assertEqual(message['id'], "simple")
        return message['id'] == "simple"

    def test_stats(self):
        """
        Test if stats are returned if config['return_stats'] is set to True
        :return:
        """
        ## Test simple response
        self._message_queue.put({'id': "stats", 'name': "test_skill",
                                 'config': {'return_stats': True},
                                 'data': time.perf_counter()})

        self._logger.info("Wait for response ...")

        message = self._client_queue.get()

        self._logger.info("Simple response time: {:3f}ms".format((time.perf_counter() - message['data']) * 1000))
        self.assertEqual(message['id'], "stats")
        self.assertTrue("stats" in message)
        self._logger.info("Simple duration time: {:3f}ms".format((time.perf_counter() - message['data']) * 1000))

    def test_config(self):
        """
        Test different keyword arguments for the config parameter
        :return:
        """
        self._message_queue.put({'id': "stats", 'name': "test_skill",
                                 'config': {'return_stats': True},
                                 'data': time.perf_counter()})
        self._message_queue.put({'id': "stats", 'name': "test_skill",
                                 'data': time.perf_counter()})
        self._message_queue.put({'id': "stats", 'name': "test_skill",
                                 'config': {},
                                 'data': time.perf_counter()})

        self._logger.info("Wait for response ...")

        message1 = self._client_queue.get()
        message2 = self._client_queue.get()
        message3 = self._client_queue.get()

        self.assertEqual(message1['id'], "stats")

    def test_attack(self):
        """
        Attacks Broker with fault requests
        :return:
        """
        self._message_queue.put({})
        self._message_queue.put("")
        self._message_queue.put([])
        self._message_queue.put("Test")
        self._message_queue.put({'1': "2"})
        self._message_queue.put([1, 2, 3])
        self._message_queue.put(1)
        self._message_queue.put(True)

        # Clear queue
        while not self._client_queue.empty():
            self._client_queue.get()

        self.assertTrue(self.test_simple_request())

    def test_guard(self):
        """
        Test if guard is working
        :return:
        """
        self._logger.info("Start client ...")
        ctx = mp.get_context('spawn')

        # TODO assert check if guard is really running
        guard = Guard("http://{}:{}".format(os.getenv("BROKER_HOST"), os.getenv("BROKER_PORT")),
                      os.getenv("BROKER_TOKEN"))
        client = ctx.Process(target=guard.run,
                             args=())
        client.start()
        client.terminate()
        client.join()

    def test_stressTest(self):
        """
        Stress test for broker with multiple clients
        :return:
        """
        self._logger.info("Start clients ...")
        num_clients = 2
        requests_per_client = 100
        client_queues = {}
        message_queues = {}
        clients = {}
        timeout = 0.01
        for i in range(num_clients):
            self._logger.debug("Start client {}".format(i))
            ctx = mp.get_context('spawn')
            client_queues[i] = mp.Manager().Queue(int(requests_per_client / 2))
            message_queues[i] = mp.Manager().Queue(int(requests_per_client / 2))
            clients[i] = ctx.Process(target=simple_client, args=(
                "http://{}:{}".format(os.getenv("BROKER_HOST"), os.getenv("BROKER_PORT")),
                os.getenv("BROKER_TOKEN"), client_queues[i], message_queues[i], "test_skill"))
            clients[i].start()

        self._logger.info("Waiting for clients to be ready ...")
        for i in range(num_clients):
            message = client_queues[i].get()
            self._logger.debug("Main process received message: {}".format(message))
        self._logger.info("Clients ready!")

        def check_queues(queues, file):
            n = 0
            for q in queues:
                try:
                    m = queues[q].get(block=False)
                    self._logger.debug("Received message: {}".format(m))
                    file.write("{}\n".format(json.dumps({"perf_counter_end": time.perf_counter(), "data": m})))
                    n += 1
                except queue.Empty:
                    pass
            return n

        self._logger.info("Start test ...")
        results = 0
        with open("./test/results.jsonl", "w") as file:
            for l in range(requests_per_client):
                for i in range(num_clients):
                    results += check_queues(client_queues, file)

                    message_queues[i].put({'id': "{}-{}".format(i, j), 'name': "test_skill",
                                           'config': {'return_stats': True},
                                           'data': {'perf_counter_start': time.perf_counter()}})

            self._logger.info("Waiting for responses ...")
            for l in range(requests_per_client):
                for i in range(num_clients):
                    try:
                        message = client_queues[i].get(timeout=timeout)
                        file.write("{}\n".format(json.dumps({"perf_counter_end": time.perf_counter(), "data": message})))
                        self._logger.debug("Main process received message: {} {}/{}".format(message, i * l,
                                                                                            requests_per_client * num_clients))
                    except queue.Empty:
                        self._logger.error(
                            "Main process received no message: {}/{}".format(i * l, requests_per_client * num_clients))
        for i in range(num_clients):
            clients[i].terminate()

        for i in range(num_clients):
            clients[i].join()


if __name__ == '__main__':
    unittest.main()
