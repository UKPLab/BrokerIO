"""
Broker entry point for bootstrapping the server

This is the file used to start the flask (and socketio) server.
"""

import random
import string

import redis
from flask import Flask, session, request
from flask_socketio import SocketIO

from . import init_logging, load_config
from .utils import connect_db
from .sockets.Auth import Auth
from .sockets.Request import Request
from .sockets.Skill import Skill


def init(args):
    """
    Initialize the flask app and check for the connection to the GROBID client.
    :return:
    """
    logger = init_logging("broker")

    # load config
    config = load_config(args.config_file)

    logger.info("Initializing server...")
    # flask server
    app = Flask("broker")
    app.config.update({
        "SECRET_KEY": ''.join(random.choice(string.printable) for i in range(8)),
        "SESSION_TYPE": "redis",
        "SESSION_PERMANENT": False,
        "SESSION_USE_SIGNER": True,
        "SESSION_REDIS": redis.from_url(args.redis_url, )
    })
    socketio = SocketIO(app, cors_allowed_origins='*', logger=logger, engineio_logger=logger)

    # get db and collection
    logger.info("Connecting to db {}...".format(args.db_url))
    db = connect_db(args, config, socketio)

    if db.first_run:
        logger.info("First run detected, initializing db...")
        from brokerio.utils import check_key

        check_key(private_key_path=args.private_key_path, create=True)
        db.users.reinit(private_key_path=args.private_key_path)

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
        "debug": args.flask_debug if args.flask_debug else False,
        "host": "0.0.0.0",
        "port": args.port
    }
    logger.info("App starting ...", app_config)
    socketio.run(app, **app_config, log_output=True)


def start(args):
    """
    Start the broker from command line
    :param args: command line arguments
    :return:
    """
    # load env
    init(args)


def scrub(args):
    """
    Scrubjob for database
    :param args: command line arguments
    :return:
    """
    from brokerio.utils import scrub_job

    scrub_job(args)


def keys_init(args):
    """
    Initialize the keys for the broker
    :param args: command line arguments
    :return:
    """
    from brokerio.utils import init_job, check_key

    check_key(private_key_path=args.private_key_path, create=True)
    init_job(args)


def assign(args):
    """
    Assign a role to a user
    :param args:
    :return:
    """
    logger = init_logging("broker_assign")

    config = load_config()
    config['cleanDbOnStart'] = False
    config['scrub']['enabled'] = False
    config['taskKiller']['enabled'] = False
    db = connect_db(config, None)

    user = db.users.set_role(args.key, args.role)
    if user:
        logger.info("Role assigned to user, db entry: {}".format(user['_key']))
    else:
        logger.error("User not found in db, please check the public key")
