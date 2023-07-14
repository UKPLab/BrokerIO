"""
Broker entry point for bootstrapping the server

This is the file used to start the flask (and socketio) server.
"""

from eventlet import monkey_patch  # mandatory! leave at the very top

monkey_patch()

import sys
from flask import Flask, session, request
from flask_socketio import SocketIO
from broker.config.WebConfiguration import instance as WebInstance

from broker.sockets.Request import Request
from broker.sockets.Skill import Skill

from broker.sockets.Auth import Auth
import os
from broker import init_logging, load_config
from broker.db.Database import Database


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
    DEV_MODE = "--dev" in sys.argv
    DEBUG_MODE = "--debug" in sys.argv
    web_config = WebInstance(dev=DEV_MODE, debug=DEBUG_MODE)
    config = load_config()

    logger.info("Initializing server...")
    # flask server
    app = Flask("broker")
    app.logger = logger
    app.config.update(web_config.flask)
    app.config.update(web_config.session)
    socketio = SocketIO(app, **web_config.socketio, logger=logger, engineio_logger=logger)

    # get db and collection
    logger.info("Connecting to db...")
    url = "http://{}:{}".format(os.getenv("ARANGODB_HOST", "localhost"), os.getenv("ARANGODB_PORT", "8529"))
    password = os.getenv("ARANGODB_ROOT_PASSWORD", "root")
    db_name = os.getenv("ARANGODB_DB_NAME", "broker")
    db = Database(url=url, username="root", password=password, db_name=db_name, config=config, socketio=socketio)

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

    logger.info("App starting ...", web_config.app)
    socketio.run(app, **web_config.app, log_output=True)


if __name__ == '__main__':
    init()
