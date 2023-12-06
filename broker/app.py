"""
Broker entry point for bootstrapping the server

This is the file used to start the flask (and socketio) server.
"""

from eventlet import monkey_patch  # mandatory! leave at the very top

monkey_patch()

from flask import Flask, session, request
from flask_socketio import SocketIO

from broker.sockets.Request import Request
from broker.sockets.Skill import Skill

from broker.sockets.Auth import Auth
import os
from broker import init_logging, load_config, load_env
from broker.db import connect_db
import random
import string
import redis

__version__ = os.getenv("BROKER_VERSION")
__author__ = "Dennis Zyska, Nils Dycke"
__credits__ = ["Dennis Zyska", "Nils Dycke"]


def init():
    """
    Initialize the flask app and check for the connection to the GROBID client.
    :return:
    """
    logger = init_logging("broker")

    # check if dev mode
    load_env()
    config = load_config()

    logger.info("Initializing server...")
    # flask server
    app = Flask("broker")
    app.config.update({
        "SECRET_KEY": ''.join(random.choice(string.printable) for i in range(8)),
        "SESSION_TYPE": "redis",
        "SESSION_PERMANENT": False,
        "SESSION_USE_SIGNER": True,
        "SESSION_REDIS": redis.from_url("redis://{}:{}".format(os.getenv("REDIS_HOST"), os.getenv("REDIS_PORT")), )
    })
    socketio = SocketIO(app, cors_allowed_origins='*', logger=logger, engineio_logger=logger)

    # get db and collection
    logger.info("Connecting to db...")
    db = connect_db(config, socketio)

    # add socket routes
    logger.info("Initializing socket...")
    sockets = {
        "request": Request(db=db, socketio=socketio),
        "auth": Auth(db=db, socketio=socketio),
        "skill": Skill(db=db, socketio=socketio)
    }

    # socketio
    @socketio.on("connect")
    def connect(data):
        """
        Example connection event. Upon connection on "/" the sid is loaded, stored in the session object
        and the connection is added to the room of that SID to enable an e2e connection.

        :return: the sid of the connection
        """
        db.clients.connect(sid=request.sid, ip=request.remote_addr, data=data)
        session["sid"] = request.sid

        logger.debug(f"New socket connection established with sid: {request.sid} and ip: {request.remote_addr}")

        return request.sid

    @socketio.on("disconnect")
    def disconnect():
        """
        Disconnection event

        :return: void
        """
        db.clients.disconnect(sid=request.sid)

        logger.debug(f"Socket connection teared down for sid: {request.sid}")

    app_config = {
        "debug": os.getenv("FLASK_DEBUG", False),
        "host": os.getenv("BROKER_HOST", "127.0.0.1"),
        "port": os.getenv("BROKER_PORT", 4852)
    }
    logger.info("App starting ...", app_config)
    socketio.run(app, **app_config, log_output=True)


if __name__ == '__main__':
    init()
