import os
import random
import time
from uuid import uuid4

import logging
from flask import session

from broker.db.Announcement import Skill, NetNode
from broker.db.Registry import Registry
from broker.db.Task import Task
from broker.utils.Quota import Quota
from . import SocketRoute


class RegisterRoute(SocketRoute):
    def __init__(self, name, socketio, registry: Registry):
        super().__init__(name, socketio)
        self.current_tasks = {}
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
        self.current_tasks[uid] = Task(task_id=uid, request_id=data['id'], session_id=sid)
        self.socketio.emit("taskRequest", {'id': uid, 'data': data['data']}, room=owner)

    def results(self, data):
        """
        Send results to client
        """
        sid = session["sid"]
        if self.quota_results(sid, append=True):
            return

        logging.debug("Get skill results after {:.3f} ms".format(
            (time.perf_counter() - self.current_tasks[data['id']].start_time) * 1000))
        logging.debug("Results: ", data)
        logging.debug("Task: ", self.current_tasks[data['id']].__dict__)

        self.socketio.emit("skillResults",
                           {'id': self.current_tasks[data['id']].request_id, 'data': data['data']},
                           room=self.current_tasks[data['id']].session_id)
        del (self.current_tasks[data['id']])
