import logging
import random
import string
import time

import socketio

from broker import init_logging


def get_random_string(length):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def simple_response_container(name, url, token, skill_name, q, roles=None, log_level="INFO"):
    logger = init_logging(name, level=logging.getLevelName(log_level))
    sio_container = socketio.Client(logger=logger, engineio_logger=logger)
    skill = {
        "name": skill_name
    }
    if roles:
        skill["roles"] = roles
    sio_container.on("connect",
                     lambda: [sio_container.emit('skillRegister', skill), q.put("connected")])
    sio_container.on("taskRequest",
                     lambda data: sio_container.emit('taskResults', {"id": data["id"], "data": data['data']}))

    while True:
        try:
            sio_container.connect(url, auth={"token": token})
            sio_container.wait()
        except socketio.exceptions.ConnectionError:
            logger.error("Connection to broker failed. Trying again in 5 seconds ...")
            time.sleep(5)
