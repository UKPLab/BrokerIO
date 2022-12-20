import logging
import multiprocessing as mp
import os
import time
import unittest

from dotenv import load_dotenv

from broker import init_logging
from broker.app import init
from broker.utils import simple_client
from broker.utils.Guard import Guard
from test.TestClient import TestClient
from test.utils import check_queue
from test.utils import simple_response_container


class TestBroker(unittest.TestCase):
    _broker = None
    _container = None
    _client = None
    _logger = None

    @classmethod
    def setUpClass(cls):
        if os.getenv("TEST_URL", None) is None:
            load_dotenv(dotenv_path=".env")
        logger = init_logging(name="Unittest", level=logging.DEBUG)
        cls._logger = logger

        logger.info("Starting response container ...")
        ctx = mp.get_context('spawn')
        container = ctx.Process(target=simple_response_container, args=(
            os.getenv("TEST_URL"), os.getenv("TEST_TOKEN"),
            "test_skill"))
        container.start()
        cls._container = container

        logger.info("Starting broker ...")
        logger.debug("Broker URL: {}".format(os.getenv("TEST_URL")))
        logger.debug("Broker Token: {}".format(os.getenv("TEST_TOKEN")))
        logger.debug("Broker Skill: {}".format("test_skill"))
        logger.debug("Start Broker? {}".format(os.getenv("TEST_START_BROKER")))
        if int(os.getenv("TEST_START_BROKER")) == 0:
            logger.info("Skip creating broker.")
        else:
            ctx = mp.get_context('spawn')
            broker = ctx.Process(target=init, args=())
            broker.start()
            cls._broker = broker

        logger.info("Starting client for testing that the environment is working ...")
        client = TestClient(logger, os.getenv("TEST_URL"), os.getenv("TEST_TOKEN"), "test_skill")
        client.start()
        logger.info("Environment ready!")
        client.stop()

    @classmethod
    def tearDownClass(cls):
        cls._logger.info("Stopping response container ...")
        cls._container.terminate()
        cls._container.join()

        cls._logger.info("Stopping broker ...")
        if int(os.getenv("TEST_START_BROKER")) == 0:
            cls._logger.info("Skip stopping broker.")
        else:
            cls._broker.terminate()
            cls._broker.join()

    def setUp(self) -> None:
        self._logger.info("Start new client ...")
        self.client = TestClient(self._logger, os.getenv("TEST_URL"), os.getenv("TEST_TOKEN"), "test_skill",
                                 2 * int(os.getenv("QUOTA_CLIENTS")))
        self.client.start()

    def tearDown(self) -> None:
        self._logger.info("Stop client ...")
        self.client.stop()

    def test_simple_request(self):
        """
        Test if a simple request is working
        :return:
        """
        self.client.put({'id': "simple", 'name': "test_skill", 'data': time.perf_counter()})

        self._logger.info("Wait for response ...")

        message = self.client.get()

        self._logger.debug("Main process received message: {}".format(message))

        self._logger.info("Simple response time: {:3f}ms".format((time.perf_counter() - message['data']) * 1000))
        self.assertEqual(message['id'], "simple")
        return message['id'] == "simple"

    def test_stats(self):
        """
        Test if stats are returned if config['return_stats'] is set to True
        :return:
        """
        ## Test simple response
        self.client.put({'id': "stats", 'name': "test_skill",
                         'config': {'return_stats': True},
                         'data': time.perf_counter()})

        self._logger.info("Wait for response ...")

        message = self.client.get()

        self._logger.info("Simple response time: {:3f}ms".format((time.perf_counter() - message['data']) * 1000))
        self.assertEqual(message['id'], "stats")
        self.assertTrue("stats" in message)
        self._logger.info("Simple duration time: {:3f}ms".format((time.perf_counter() - message['data']) * 1000))

    def test_config(self):
        """
        Test different keyword arguments for the config parameter
        :return:
        """
        self.client.put({'id': "stats", 'name': "test_skill",
                         'config': {'return_stats': True},
                         'data': time.perf_counter()})
        self.client.put({'id': "stats", 'name': "test_skill",
                         'data': time.perf_counter()})
        self.client.put({'id': "stats", 'name': "test_skill",
                         'config': {},
                         'data': time.perf_counter()})

        self._logger.info("Wait for response ...")

        message1 = self.client.get()
        message2 = self.client.get()
        message3 = self.client.get()

        self.assertEqual(message1['id'], "stats")
        self.assertEqual(message2['id'], "stats")
        self.assertEqual(message3['id'], "stats")

    def test_attack(self):
        """
        Attacks Broker with fault requests
        :return:
        """
        self.client.put({})
        self.client.put("")
        self.client.put([])
        self.client.put("Test")
        self.client.put({'1': "2"})
        self.client.put([1, 2, 3])
        self.client.put(1)
        self.client.put(True)

        self.client.clear()

        self.assertTrue(self.test_simple_request())

    def test_guard(self):
        """
        Test if guard is working
        :return:
        """
        self._logger.info("Start client ...")
        ctx = mp.get_context('spawn')

        # TODO assert check if guard is really running
        guard = Guard(os.getenv("TEST_URL"), os.getenv("TEST_TOKEN"))
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
        delay = 0.06  # Due to quota limit

        for i in range(num_clients):
            self._logger.debug("Start client {}".format(i))
            ctx = mp.get_context('spawn')
            client_queues[i] = mp.Manager().Queue(int(requests_per_client / 2))
            message_queues[i] = mp.Manager().Queue(int(requests_per_client / 2))
            clients[i] = ctx.Process(target=simple_client, args=("Client_{}".format(i),
                                                                 os.getenv("TEST_URL"),
                                                                 os.getenv("TEST_TOKEN"), client_queues[i],
                                                                 message_queues[i], "test_skill"))
            clients[i].start()

        self._logger.info("Waiting for clients to be ready ...")
        for i in range(num_clients):
            message = client_queues[i].get()
            self._logger.debug("Main process received message: {}".format(message))
        self._logger.info("Clients ready!")

        self._logger.info("Start test ...")
        results = 0
        with open("./test/results.jsonl", "w") as file:
            for l in range(requests_per_client):
                for i in range(num_clients):
                    if check_queue(client_queues[i], file):
                        results += 1

                    message_queues[i].put({'id': "{}-{}".format(i, l), 'name': "test_skill",
                                           'config': {'return_stats': True},
                                           'data': {'perf_counter_start': time.perf_counter()}})
                time.sleep(delay)

            self._logger.info("Check if there are open responses?")
            end = time.perf_counter() + timeout
            while results < requests_per_client * num_clients and time.perf_counter() < end:
                for i in range(num_clients):
                    if check_queue(client_queues[i], file):
                        results += 1

            if results < requests_per_client * num_clients:
                self._logger.error("Not all responses received!")
            else:
                self._logger.info("All responses received!")

            self.assertEqual(results, requests_per_client * num_clients)

        for i in range(num_clients):
            clients[i].terminate()

        for i in range(num_clients):
            clients[i].join()

    def test_quota(self):
        """
        Check if quota is working
        :return:
        """

        self._logger.info("Start new client ...")
        ctx = mp.get_context('spawn')
        c_queue = mp.Manager().Queue(2 * int(os.getenv("QUOTA_CLIENTS")))
        m_queue = mp.Manager().Queue(2 * int(os.getenv("QUOTA_CLIENTS")))
        client = ctx.Process(target=simple_client, args=("TestClient",
                                                         os.getenv("TEST_URL"),
                                                         os.getenv("TEST_TOKEN"), c_queue, m_queue, "test_skill"))
        client.start()

        results = 0
        start = time.perf_counter()
        while time.perf_counter() - start < 1:
            m_queue.put({'id': "quota", 'name': "test_skill",
                         'config': {'return_stats': True},
                         'data': time.perf_counter()})

        timeout = time.perf_counter() + 3
        while time.perf_counter() < timeout:
            if check_queue(c_queue):
                results += 1

        self._logger.debug("Stop client ...")
        client.terminate()
        client.join()

        self.assertEqual(int(os.getenv("QUOTA_CLIENTS")), results)

    def test_delay(self):
        """
        Check if simulated delay is working
        :return:
        """
        self.client.put({'id': "delay", 'name': "test_skill",
                         'config': {'min_delay': 1, "return_stats": True},  # 500ms
                         'data': time.perf_counter()})

        self._logger.info("Sending request in between ...")
        time.sleep(0.01)
        self.client.put({'id': "between", 'name': "test_skill",
                         'config': {"return_stats": True},
                         'data': time.perf_counter()})

        message = self.client.get()
        self._logger.debug("Main process received message: {}".format(message))
        self.assertEqual(message['id'], "between")

        message = self.client.get()
        self._logger.debug("Main process received message: {}".format(message))
        self.assertEqual(message['id'], "delay")
        self.assertGreater(time.perf_counter() - message['data'], 1)


if __name__ == '__main__':
    unittest.main()
