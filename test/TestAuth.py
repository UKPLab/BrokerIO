import logging
import multiprocessing as mp
import time

import socketio

from broker import init_logging
from broker.utils.Keys import Keys


def auth_client(url, queue: mp.Queue):
    logger = init_logging("Auth Client", level=logging.getLevelName("INFO"))
    sio = socketio.Client(logger=logger, engineio_logger=logger)
    keys = Keys(private_key_path="./private_key.pem")

    @sio.on('authChallenge')
    def task(data):
        logger.info("authChallenge data: {}".format(data))
        sig = keys.sign(data['secret'])
        sio.emit('authResponse', {'pub': keys.get_public(), 'sig': sig})

    @sio.on('authInfo')
    def info(data):
        logger.info("authInfo data: {}".format(data))
        queue.put(data['role'])

    sio.on('connect', lambda: [sio.emit('authRequest')])

    while True:
        try:
            if sio.connected:
                logger.debug("Waiting for next message...")
            else:
                sio.connect(url)
        except socketio.exceptions.ConnectionError:
            logger.error("Connection to broker failed. Trying again in 5 seconds ...")
            time.sleep(5)


class TestAuth:
    def __init__(self, logger, url):
        self.url = url
        self.logger = logger
        self.queue = mp.Manager().Queue(5)

    def test(self):
        self.logger.info("Start auth client ...")
        ctx = mp.get_context('spawn')
        self.client = ctx.Process(target=auth_client, args=(self.url, self.queue))
        self.client.start()
        return self.queue.get()

    def terminate(self):
        self.client.terminate()
        self.client.join()
