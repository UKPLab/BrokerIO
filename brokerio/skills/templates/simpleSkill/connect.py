""" Providing a simple template for a skill service to the broker

This file is an example to provide a nlp model service to the broker
and publish the skills of the model.
It can be adapted to the use case of the model.

For socketio, see https://python-socketio.readthedocs.io

Author: Dennis Zyska
"""
import logging
import os
import time

import socketio
from Skill import Skill

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info("Create SocketIO Client...")
    sio = socketio.Client()

    logging.info("Init skill...")
    skill = Skill()
    skill.set_sio(sio)
    skill.init()


    @sio.on('error')
    def error(data):
        logging.error("Received error: {}".format(data))


    @sio.on("taskRequest")
    def task(data):
        logging.info("Received new task: {}".format(data))
        try:
            output, stats = skill.execute(data['id'], data['data'])
            logging.info("Output: {}".format(output))
            logging.info("Stats: {}".format(stats))

            result = {'id': data['id'], 'data': output}
            if stats is not None:
                result['stats'] = stats
            sio.emit('taskResults', result)
        except Exception as err:
            logging.error("Error in task {}: {}".format("taskRequest", data))
            logging.error(err)
            output = {
                'code': 112,
                'clientId': data['clientId'] if 'clientId' in data else None,
                'message': str(err)
            }
            sio.emit('taskResults', {'id': data['id'], 'error': output})


    @sio.on('connect')
    def connect():
        logging.info('Connection established!')
        sio.emit('skillRegister', skill.get_config())


    logging.info("Connect to broker...")
    while True:
        try:
            logging.info("Connect to broker {}".format(os.environ.get('BROKER_URL')))
            sio.connect(os.environ.get('BROKER_URL'))
            sio.wait()
        except Exception as e:
            logging.error(e)
            logging.error("Connection to broker failed. Trying again in 5 seconds ...")
            time.sleep(5)
