import os
import random
from uuid import uuid4

from flask import session

from broker.db.Announcement import Skill, NetNode
from broker.db.Registry import Registry
from . import SocketRoute
from broker.utils.Quota import Quota


class RegisterRoute(SocketRoute):
    def __init__(self, name, socketio, registry: Registry):
        super().__init__(name, socketio)
        self.client_skill_mapping = {}
        self.quota = Quota(max_len=int(os.getenv("QUOTA_CLIENTS", 20)))
        self.quota_results = Quota(max_len=int(os.getenv("QUOTA_RESULTS", 100)))
        self.registry = registry

    def _init(self):
        self.socketio.on_event("skillRegister", self.register)
        self.socketio.on_event("skillGetAll", self.get_all)
        self.socketio.on_event("skillGetConfig", self.get_config)
        self.socketio.on_event("skillRequest", self.request)
        self.socketio.on_event("taskResults", self.results)

    def register(self, data):
        """
        Registers a skill on the broker.

        :param data: Data Object
        """
        sid = session["sid"]
        if self.quota(sid, append=True):
            return

        # currently we simply copy everything trusting the source
        skill = Skill(data)
        owner = NetNode(sid)

        self.registry.announce_skill(skill, owner)

        update_skill = self.registry.get_skill(skill.config['name'], with_config=False)
        self.socketio.emit("skillUpdate", [update_skill], broadcast=True, include_self=False)

    def get_all(self):
        """
        Informs the client about all skills currently registered on the broker.

        This should be called after a client connects to the broker. Further updates are provided by the
        "skillRegister" event.
        """
        sid = session["sid"]
        if self.quota(sid, append=True):
            return

        skills = list(self.registry.get_skills(with_config=False).values())
        self.socketio.emit("skillUpdate", skills, room=session["sid"])

    def get_config(self, data):
        """
        Get configuration from a skill by name
        """
        sid = session["sid"]
        if self.quota(sid, append=True):
            return

        skill_name = data['name']
        skill = self.registry.get_skill(skill_name)
        self.socketio.emit("skillConfig", skill, room=session["sid"])

    def request(self, data):
        """
        Request a specific skill by name
        """
        sid = session["sid"]
        if self.quota(sid, append=True):
            return

        # get all available nodes for skill; get a random owner from the list
        owners = [a["owner"]["session_id"] for a in self.registry.get_entries() if a["skill"]["name"] == data["name"]]
        owner = random.choice(owners)

        # request skill of the owner
        uid = str(uuid4())
        self.client_skill_mapping[uid] = {"sessionId": sid, "requestId": data["id"]}
        self.socketio.emit("taskRequest", {'id': uid, 'data': data['data']}, room=owner)

    def results(self, data):
        """
        Send results to client
        """
        sid = session["sid"]
        if self.quota_results(sid, append=True):
            return

        print(self.client_skill_mapping[data['id']])
        self.socketio.emit("skillResults",
                           {'id': self.client_skill_mapping[data['id']]['requestId'], 'data': data['data']},
                           room=self.client_skill_mapping[data['id']]['sessionId'])
        del(self.client_skill_mapping[data['id']])
