import os

from .Database import Database


def connect_db(args=None, config=None, socketio=None):
    """
    Connect to the arango db with environment variables.
    :return:
    """
    if args is None:
        args = {
            "db_url": "http://{}:{}".format(os.getenv("ARANGODB_HOST", "localhost"),
                                            os.getenv("ARANGODB_PORT", "8529")),
            "db_user": os.getenv("ARANGODB_USER", "root"),
            "db_pass": os.getenv("ARANGODB_PASSWORD", "secure"),
            "db_name": os.getenv("ARANGODB_DB", "broker"),
        }
        db = Database(url=args["db_url"], username=args["db_user"], password=args["db_pass"], db_name=args["db_name"],
                      config=config, socketio=socketio)
    else:
        db = Database(url=args.db_url, username=args.db_user, password=args.db_pass, db_name=args.db_name,
                      config=config,
                      socketio=socketio)
    return db
