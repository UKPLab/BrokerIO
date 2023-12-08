""" Providing a simple template for a skill service to the broker

This file is an example to provide a nlp model service to the broker
and publish the skills of the model.
It can be adapted to the use case of the model.

For socketio, see https://python-socketio.readthedocs.io

Author: Dennis Zyska
"""
import logging
import time

import socketio
import yaml

if __name__ == '__main__':
    logging.info("Create SocketIO Client...")
    sio = socketio.Client()
    @sio.on("taskRequest")
    def task(data):
        logging.info("Received new task: {}".format(data))
        try:
            print("Received new task: {}".format(data))
            # TODO: process task
        except Exception as e:
            logging.error("Error while processing task: {}".format(e))

    @sio.on('connect')
    def connect():
        logging.info('Connection established!')
        # TODO send skill config
        sio.emit('skillRegister', skill)

    logging.info("Connect to broker...")
    while True:
        try:
            logging.info("Connect to broker {}".format(config["broker_url"]))
            sio.connect(config["broker_url"])
            sio.wait()
        except:
            logging.error("Connection to broker failed. Trying again in 5 seconds ...")
            time.sleep(5)