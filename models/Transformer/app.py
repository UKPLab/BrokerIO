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


if __name__ == '__main__':
    print("Load environment variables...")
    load_dotenv()

    print("Setting up logger to level {}...".format(os.getenv("LOG_LEVEL")))
    logging.basicConfig( level=os.getenv("LOG_LEVEL").upper() )

    logging.info("Create SocketIO Client...")
    sio = socketio.Client()

    logging.info("Loading model...")
    # TODO load model and checkpoint
    # see https://pytorch-lightning.readthedocs.io/en/stable/deploy/production_intermediate.html
    model = MyModel()
    checkpoint = torch.load(os.getenv("MODEL_PATH"))
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    @sio.on('connect')
    def connect():
        logging.info('Connection established!')
        sio.emit('register', 'Transformer')

    logging.info("Connect to broker...");
    while(True):
        try:
            logging.info("Connect to broker {}".format(os.getenv("BROKER_URL")));
            sio.connect(os.getenv('BROKER_URL'), auth= { "token": os.getenv('BROKER_TOKEN')} )
            sio.wait()
        except:
            logging.error("Connection to broker failed. Trying again in 5 seconds ...")
            time.sleep(5)