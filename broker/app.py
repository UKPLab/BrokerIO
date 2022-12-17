""" app -- Bootstrapping the server

This is the file used to start the flask (and socketio) server. It is also the file considered
by the celery client to setup RPCs to the celery server.

At the moment, the file contains examples to test your setup and get a feeling for how
celery + socketio can work together.

Author: Nils Dycke, Dennis Zyska
"""
import os
import sys

from eventlet import monkey_patch  # mandatory! leave at the very top

monkey_patch()

from flask import Flask, session, request
from flask_socketio import SocketIO, join_room
from broker.config.WebConfiguration import instance as WebInstance
from broker.db.Registry import Registry
from broker.sockets.RegisterRoute import RegisterRoute


def init():
    """
    Initialize the flask app and check for the connection to the GROBID client.
    :return:
    """
    # check if dev mode
    DEV_MODE = "--dev" in sys.argv
    DEBUG_MODE = "--debug" in sys.argv
    config = WebInstance(dev=DEV_MODE, debug=DEBUG_MODE)

    print("Initializing server")
    # flask server
    app = Flask("broker")
    app.config.update(config.flask)
    app.config.update(config.session)
    socketio = SocketIO(app, **config.socketio)

    # connect to registry
    registry = Registry(os.getenv("REDIS_HOST"), os.getenv("REDIS_PORT"))
    registry.connect()
    registry.clean()

    # add socket routes
    routes = RegisterRoute("register", socketio, registry)

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
        print(data)

        # check simple authentication
        if "token" in data and os.getenv("BROKER_TOKEN", "this_is_a_random_token_to_verify") != data["token"]:
            raise ConnectionRefusedError('Authentication failed: Token invalid!')

        sid = request.sid
        session["sid"] = sid
        join_room(sid)

        print(f"New socket connection established with sid: {sid} and ip: {request.remote_addr}")

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

        # close connection
        sid = request.sid
        socketio.close_room(sid)
        # delete quota for sid
        routes.quota.delete(sid)
        routes.quota_results.delete(sid)

        # Removes owner on skill disconnection and inform other nodes
        a = registry.remove_owner(sid)
        print(a)
        if a is not None:
            skill = registry.get_skill(a['skill']['name'], with_config=False)
            socketio.emit("skillUpdate", [skill], broadcast=True, include_self=False)

        # Terminate running jobs
        # 1. Docker container disconnect
        # TODO send task eventually to the next node if available
        # 2. Client disconnect
        # TODO send cancel request via socket io emit to container

        print(f"Socket connection teared down for sid: {sid}")

    print("App starting", config.app)
    socketio.run(app, **config.app, log_output=True)


if __name__ == '__main__':
    init()
