import logging
import multiprocessing as mp
import time

import socketio

from broker import init_logging


def simple_client(url, token, client_queue: mp.Queue, message_queue: mp.Queue, skill_name="test_skill"):
    logger = init_logging("MainClient", logging.DEBUG)
    sio = socketio.Client(logger=logger)
    initialized = False

    @sio.on('skillUpdate')
    def skill_set(data):
        logger.debug("skillUpdate: {}".format(data))
        if len(data) > 0:
            for skill in data:
                if skill['name'] == skill_name:
                    sio.emit('skillGetConfig', {'name': skill['name']})

    def skill_config(data, init):
        logger.debug("skillConfig: {}".format(data))
        if data['name'] == skill_name:
            client_queue.put(data)

    sio.on('connect', lambda: sio.emit('skillGetAll'))
    sio.on('skillConfig', lambda data: skill_config(data, initialized))
    sio.on('skillResults', lambda data: [logger.debug("Skill results: {}".format(data)), client_queue.put(data)])

    # connect to Broker
    while True:
        if sio.connected:
            logger.info("Waiting for next message...")
            message = message_queue.get()
            sio.emit('skillRequest', message)
            logger.debug("Send message: {}".format(message))
        else:
            try:
                sio.connect(url, auth={"token": token})
            except socketio.exceptions.ConnectionError:
                logger.info("Connection to broker failed. Trying again in 5 seconds ...")
                time.sleep(5)


