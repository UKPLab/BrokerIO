import os
import time

from arango import ArangoClient


def connect_db():
    """
    Connects to arangodb
    :return: db instance
    """
    db_client = ArangoClient(
        hosts="http://{}:{}".format(os.getenv("ARANGODB_HOST", "localhost"), os.getenv("ARANGODB_PORT", "8529")))
    sys_db = db_client.db('_system', username='root', password=os.getenv("ARANGODB_ROOT_PASSWORD", "root"))
    if not sys_db.has_database(os.getenv("ARANGODB_DB_NAME", "broker")):
        sys_db.create_database(os.getenv("ARANGODB_DB_NAME", "broker"))
    sync_db = db_client.db(os.getenv("ARANGODB_DB_NAME", "broker"), username='root', password=os.getenv("ARANGODB_ROOT_PASSWORD", "root"))
    db = sync_db.begin_async_execution(return_result=True)
    return db, sync_db, sys_db


def results(job):
    """Return the job result of an arango db async operation.
    """
    while job.status() == "pending":
        time.sleep(0.01)

    return job.result()
