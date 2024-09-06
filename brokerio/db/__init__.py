from .Database import Database


def connect_db(args, config, socketio):
    """
    Connect to the arango db with environment variables.
    :return:
    """
    return Database(url=args.db_url, username=args.db_user, password=args.db_pass, db_name=args.db_name,
                    config=config,
                    socketio=socketio)
