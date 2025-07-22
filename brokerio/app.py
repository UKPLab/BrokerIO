"""
Broker entry point for bootstrapping the server

This is the file used to start the flask (and socketio) server.
"""
from aiohttp import web
import socketio
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

    mgr = socketio.RedisManager(args.redis_url)
    max_buffer_size = config.get('max_http_buffer_size', 5242880)
    sio = socketio.AsyncServer(mgr=mgr, cors_allowed_origins=[], async_mode='aiohttp', async_handlers=True, max_http_buffer_size=max_buffer_size)
    app = web.Application()
    sio.attach(app)

    # get db and collection
    logger.info("Connecting to db {}...".format(args.db_url))
    db = connect_db(args, config, sio)

    if db.first_run:
        logger.info("First run detected, initializing db...")
        from brokerio.utils import check_key

        check_key(private_key_path=args.private_key_path, create=True)
        db.users.reinit(private_key_path=args.private_key_path)

    # add socket routes
    logger.info("Initializing socket...")
    sockets = {
        "request": Request(db=db, socketio=sio),
        "auth": Auth(db=db, socketio=sio),
        "skill": Skill(db=db, socketio=sio)
    }

    # socketio
    @sio.on("connect")
    async def connect(sid, wsgi, data=None):
        """
        Example connection event. Upon connection on "/" the sid is loaded, stored in the session object
        and the connection is added to the room of that SID to enable an e2e connection.

        :return: the sid of the connection
        """
        await db.clients.connect(sid=sid, ip=wsgi['REMOTE_ADDR'])

        logger.debug(f"New socket connection established with sid: {sid} and ip: {wsgi['REMOTE_ADDR']}")

        #return request.sid

    @sio.on("disconnect")
    async def disconnect(sid):
        """
        Disconnection event

        :return: void
        """
        await db.clients.disconnect(sid=sid)

        logger.debug(f"Socket connection teared down for sid: {sid}")

    web.run_app(app, host='0.0.0.0', port=args.port)


def start(args):
    """
    Start the broker from command line
    :param args: command line arguments
    :return:
    """
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
