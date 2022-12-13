import json
import os

from flask import session

from broker.celery_app import request_skill_by_uid
from broker.db.registry import Registry
from broker.db.skill import Skill, NetNode
from . import SocketRoute


class RegisterRoute(SocketRoute):
    def __init__(self, name, socketio, celery):
        super().__init__(name, socketio, celery)
        self.registry = Registry(os.getenv("REDIS_HOST"), os.getenv("REDIS_PORT"))
        self.registry.connect()

    def _init(self):
        self.socketio.on_event("skillRegister", self.register)
        self.socketio.on_event("skillGetAll", self.inform)
        self.socketio.on_event("skillRequest", self.request)

    def register(self, data):
        """
        Registers a skill on the broker.

        :param data: Data Object
        """
        sid = session["sid"]

        # currently we simply copy everything trusting the source
        skill = Skill(data["name"], data)
        owner = NetNode(sid)

        registry.announce_skill(skill, owner)

        # todo: send skill information to all connected clients

    def inform(self):
        """
        Informs the client about all skills currently registered on the broker.

        This should be called after a client connects to the broker. Further updates are provided by the
        "skillRegister" event.
        """
        # todo could get quite large, if we transfer the whole config on inform call...

        announcements = registry.get_entries()
        self.socketio.emit("skillUpdate", json.dumps([a.to_dict() for a in announcements]), room=session["sid"])

    def request(self, data):
        sid = session["sid"]

        # todo distribute to suitable method depending on the data payload (for now: default by uid)

        # get skill request information
        request_skill_by_uid.delay(sid, data)
