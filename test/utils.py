import logging
import random
import string
import time
import json
import multiprocessing as mp
import socketio

from broker import init_logging


def get_random_string(length):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def set_skills(skills, data):
    if len(data) > 0:
        for skill in data:
            skills[skill['name']] = skill
    return skills


def simple_response_container(url, token, skill_name):
    logger = init_logging("ResponseContainer", logging.DEBUG)
    sio_container = socketio.Client(logger=logger)

    @sio_container.on('connect')
    def connection():
        sio_container.emit('skillRegister', {"name": skill_name})

    @sio_container.on("taskRequest")
    def task(data):
        sio_container.emit('taskResults', {'id': data['id'], 'data': data['data']})

    # connect to Broker
    while True:
        try:
            sio_container.connect(url, auth={"token": token})
            sio_container.wait()
        except socketio.exceptions.ConnectionError:
            logger.info("Connection to broker failed. Trying again in 5 seconds ...")
            time.sleep(5)


