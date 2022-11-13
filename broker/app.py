""" app -- Bootstrapping the server

This is the file used to start the flask (and socketio) server. It is also the file considered
by the celery client to setup RPCs to the celery server.

At the moment, the file contains examples to test your setup and get a feeling for how
celery + socketio can work together.

Author: Nils Dycke (dycke@ukp...)
"""
from eventlet import monkey_patch  # mandatory! leave at the very top
monkey_patch()

from flask import Flask, session, request
from flask_socketio import SocketIO, join_room, emit
from celery_app import *

from db.registry import registry
from sockets.register import RegisterRoute

# config loaded in celery_app

# flask server
app = Flask("peer_nlp")
app.config.update(config.flask)
app.config.update(config.session)
app.config.update(config.celery)  # necessary as we access the broker information later on

# socketio
socketio = SocketIO(app, **config.socketio)


def init():
    """
    Initialize the flask app and check for the connection to the GROBID client.
    :return:
    """
    print("Initializing server")

    # connect to registry
    registry.connect()

    # load token
    token = os.getenv("BROKER_TOKEN")
    if not token:
        print("No secret token provided in environment. Loading default token...")
    else:
        print("Initialized secret token from environment...")

    token = token if token else "this_is_a_random_token_to_verify"

    # add socket routes
    RegisterRoute("register", socketio, celery)

    # socketio
    @socketio.on("connect")
    def connect(data):
        """
        Example connection event. Upon connection on "/" the sid is loaded, stored in the session object
        and the connection is added to the room of that SID to enable an e2e connection.

        :return: the sid of the connection
        """
        if data is None:
            raise ConnectionRefusedError('Authentication data required on connect!')

        dtoken = data["token"]
        if dtoken != token:
            raise ConnectionRefusedError('Authentication failed: Token invalid!')

        sid = request.sid
        session["sid"] = sid
        join_room(sid)

        print(f"New socket connection established with sid: {sid}")

        return sid

    @socketio.on("disconnect")
    def disconnect():
        """
        Disconnection event

        :return: void
        """
        # todo
        # terminate running jobs
        # clear pending results

        sid = request.sid
        socketio.close_room(sid)
        print(f"Socket connection teared down for sid: {sid}")


if __name__ == '__main__':
    # this method is called when starting the flask server, initializing it to listen to WS requests
    init()
    print("App starting", config.app)
    socketio.run(app, **config.app, log_output=True)