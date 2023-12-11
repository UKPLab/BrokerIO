""" app -- Providing a nlp model service to the broker

This file is an example to provide a nlp model service to the broker
and publish the skills of the model.
It can be adapted to the use case of the model.

For socketio, see https://python-socketio.readthedocs.io

Author: Dennis Zyska, Paul Schickling
"""
import logging
import time

import socketio
import yaml
from llama_cpp import Llama

if __name__ == '__main__':
    print("Load config...")
    with open("./config/config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        print("Config loaded: {}".format(config))

    print("Load skill config...")
    with open("./config/sdf.yaml", "r") as f:
        skill = yaml.load(f, Loader=yaml.FullLoader)
        print("Skill config loaded: {}".format(skill))

    logging.info("Create SocketIO Client...")
    sio = socketio.Client()

    logging.info("Load llama model {}...".format(config["model_path"]))
    llm = Llama(config["model_path"], n_threads=config['num_threads'], n_ctx=config['num_ctx'])

    @sio.on("taskRequest")
    def task(data):
        logging.info("Received new task: {}".format(data))
        try:
            sio.emit('taskResults', {'id': data['id'], 'data': llm(data['data'])})
            if 'grammar' in data['data'].keys():
                from llama_cpp.llama import Llama, LlamaGrammar
                data['data']['grammar'] = LlamaGrammar.from_string(data['data']['grammar'])
            sio.emit('taskResults', {'id': data['id'], 'data': llm(data['data']['prompt'], **data['data']['params'])})
        except Exception as e:
            logging.error("Error while processing task: {}".format(e))
            sio.emit('taskResults', {'id': data['id'], 'data': {'error': str(e)}})

    @sio.on('connect')
    def connect():
        logging.info('Connection established!')
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
