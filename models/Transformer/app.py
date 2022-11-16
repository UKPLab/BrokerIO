""" app -- Providing a nlp model service to the broker

This file is an example to provide a nlp model service to the broker
and publish the skills of the model.
It can be adapted to the use case of the model.

For socketio, see https://python-socketio.readthedocs.io

Author: Dennis Zyska (zyska@ukp...)
"""
import socketio
import os
from dotenv import load_dotenv
import time
import logging
import torch
import yaml
from transformers import pipeline

if __name__ == '__main__':
    print("Load environment variables...")
    load_dotenv()

    print("Setting up logger to level {}...".format(os.getenv("LOG_LEVEL")))
    logging.basicConfig(level=os.getenv("LOG_LEVEL").upper())

    print("Load skill config...")
    with open(os.getenv("SKILL_FILE"), "r") as f:
        skill = yaml.safe_load(f)

    logging.info("Create SocketIO Client...")
    sio = socketio.Client()

    logging.info("Transformers pipeline...")
    pipe = pipeline(**skill['pipeline'])

    @sio.on("task")
    def task(data):
        logging.info("Received new task: {}".format(data))
        sio.emit('results', {'task_id': data['task_id'], 'results': pipe(data['data'])})


    @sio.on('connect')
    def connect():
        logging.info('Connection established!')
        sio.emit('register_skill', skill)


    logging.info("Connect to broker...")
    while True:
        try:
            logging.info("Connect to broker {}".format(os.getenv("BROKER_URL")))
            sio.connect(os.getenv('BROKER_URL'), auth={"token": os.getenv('BROKER_TOKEN')})
            sio.wait()
        except:
            logging.error("Connection to broker failed. Trying again in 5 seconds ...")
            time.sleep(5)
