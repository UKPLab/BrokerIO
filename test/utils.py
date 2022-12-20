import json
import logging
import queue
import random
import string
import time

import socketio

from broker import init_logging

def check_queue(q, fp=None):
    try:
        m = q.get(block=False)
        if fp:
            fp.write("{}\n".format(json.dumps({"perf_counter_end": time.perf_counter(), "data": m})))
        return True
    except queue.Empty:
        return False


def get_random_string(length):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def simple_response_container(url, token, skill_name):
    logger = init_logging("ResponseContainer", logging.DEBUG)
    sio_container = socketio.Client(logger=logger)
    sio_container.on("connect", lambda: sio_container.emit('skillRegister', {"name": skill_name}))
    sio_container.on("taskRequest",
                     lambda data: sio_container.emit('taskResults', {"id": data["id"], "data": data['data']}))

    while True:
        try:
            sio_container.connect(url, auth={"token": token})
            sio_container.wait()
        except socketio.exceptions.ConnectionError:
            logger.error("Connection to broker failed. Trying again in 5 seconds ...")
            time.sleep(5)
