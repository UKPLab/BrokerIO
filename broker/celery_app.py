from eventlet import monkey_patch  # mandatory! leave at the very top
monkey_patch()

import hashlib
import json
import os

from broker.config.WebConfiguration import WebConfiguration, instance as WebInstance

import sys
from celery import Celery
from flask_socketio import SocketIO

# check if dev mode
DEV_MODE = "--dev" in sys.argv
DEBUG_MODE = "--debug" in sys.argv

# load default web server configuration
config = WebInstance(dev=DEV_MODE, debug=DEBUG_MODE)

# celery
celery = Celery("peer_nlp", **config.celery)
celery.conf.update(config.flask)
celery.conf.update(config.session)


@celery.task
def request_skill_by_uid(sid, req):
    socket = SocketIO(message_queue=config.celery["broker"])

    # connect to the registry
    from db.registry import registry
    registry.connect()

    # get the skill and associated owner
    skill = registry.get_entry(req["skill_uid"])
    osid = skill.owner

    # TODO add an unique id to the request

    # request and wait #todo check that this works properly
    res = socket.call("taskRequest", req, namespace=osid)

    # send response and terminate
    socket.emit("taskResults", res, room=sid)
