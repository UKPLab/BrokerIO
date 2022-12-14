import json
import os
import random

from flask import session

from broker.celery_app import request_skill_by_uid, request_skill_by_owner_id
from broker.db.Registry import Registry
from broker.db.Announcement import Skill, NetNode
from . import SocketRoute


class RegisterRoute(SocketRoute):
    def __init__(self, name, socketio, celery):
        super().__init__(name, socketio, celery)
        self.registry = Registry(os.getenv("REDIS_HOST"), os.getenv("REDIS_PORT"))
        self.registry.connect()

    def _init(self):
        self.socketio.on_event("skillRegister", self.register)
        self.socketio.on_event("skillGetAll", self.get_all)
        self.socketio.on_event("skillGetConfig", self.get_config)
        self.socketio.on_event("skillRequest", self.request)

    def register(self, data):
        """
        Registers a skill on the broker.

        :param data: Data Object
        """
        sid = session["sid"]

        # currently we simply copy everything trusting the source
        skill = Skill(data)
        owner = NetNode(sid)

        self.registry.announce_skill(skill, owner)

        # todo: send skill information to all connected clients

    def get_all(self):
        """
        Informs the client about all skills currently registered on the broker.

        This should be called after a client connects to the broker. Further updates are provided by the
        "skillRegister" event.
        """
        skills = list(self.registry.get_skills(with_config=False).values())
        self.socketio.emit("skillUpdate", skills, room=session["sid"])

    def get_config(self, data):
        """
        Get configuration from a skill by name
        """
        skill_name = data['name']
        skill = self.registry.get_skill(skill_name)
        self.socketio.emit("skillConfig", skill, room=session["sid"])

    def request(self, data):
        """
        Request a specific skill by name
        """
        sid = session["sid"]

        # get all available nodes for skill; get a random owner from the list
        owners = [a["owner"]["session_id"] for a in self.registry.get_entries() if a["skill"]["name"] == data["name"]]
        owner = random.choice(owners)

        # request skill of the owner
        request_skill_by_owner_id.delay(sid, owner, data["data"])
