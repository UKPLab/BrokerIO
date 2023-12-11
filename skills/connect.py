""" Providing a simple template for a skill service to the broker

This file is an example to provide a nlp model service to the broker
and publish the skills of the model.
It can be adapted to the use case of the model.

For socketio, see https://python-socketio.readthedocs.io

Author: Dennis Zyska
"""
import importlib
import logging
import os
import time

import socketio
import yaml

from Skill import Skill

if __name__ == '__main__':
    logging.info("Create SocketIO Client...")
    sio = socketio.Client()

    logging.info("Load skill config...")
    with open("./app/sdf.yaml", "r") as f:
        skill_config = yaml.load(f, Loader=yaml.FullLoader)
        print("Skill config loaded: {}".format(skill_config))

    logging.info("Init skill...")
    skill = Skill(skill_config)
    skill.init()

    @sio.on("taskRequest")
    def task(data):
        logging.info("Received new task: {}".format(data))
        try:
            sio.emit('taskResults', {'id': data['id'], 'data': skill.execute(data)})
        except Exception as e:
            logging.error("Error while processing task: {}".format(e))


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
